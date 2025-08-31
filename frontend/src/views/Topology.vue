<template>
  <div class="clustered-graph-container">
    <h1 class="graph-title"></h1>

    <!-- Search Bar -->
    <div class="search-container">
      <div class="search-input-wrapper">
        <input
          v-model="searchTerm"
          @input="handleSearch"
          type="text"
          placeholder="Search anime/manga titles..."
          class="search-input"
        />
        <div v-if="searchResults.length > 0 && searchTerm" class="search-results">
          <div
            v-for="result in searchResults.slice(0, 10)"
            :key="result.id"
            @click="focusOnNode(result)"
            class="search-result-item"
          >
            <div class="search-result-title">
              {{ result.label || result.name || `${result.type} ${result.id}` }}
            </div>
            <div class="search-result-subtitle">
              {{ result.clusterName || 'Standalone' }} •
              {{ result.connectionCount || 0 }} connections
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <div>Clustering relations...</div>
      <div class="loading-subtitle">
        Found {{ totalClusters }} clusters from {{ totalNodes }} nodes
      </div>
      <div v-if="progressText" class="loading-subtitle">{{ progressText }}</div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-container" style="color: red; padding: 20px">
      Error: {{ error }}
    </div>

    <!-- Main Graph -->
    <div v-else class="graph-wrapper">
      <!-- Main SVG Container -->
      <div class="canvas-container">
        <div class="starfield-background"></div>
        <svg
          ref="svgRef"
          class="graph-svg"
          :viewBox="`0 0 ${svgDimensions.width} ${svgDimensions.height}`"
        ></svg>

        <!-- Minimap -->
        <div class="minimap-container">
          <svg
            ref="minimapRef"
            width="150"
            height="100"
            class="minimap-svg"
            @click="handleMinimapClick"
          ></svg>
        </div>
      </div>

      <!-- Info Panel -->
      <div class="info-panel">
        <div><strong>Hierarchical View</strong></div>
        <div>Level: {{ currentViewLevel }}</div>
        <div>Zoom: {{ zoomLevel.toFixed(1) }}x</div>
        <div>Visible: {{ visibleElementsCount }} elements</div>
        <div>Total Clusters: {{ totalClusters }}</div>
        <div class="legend">
          <div>
            <span class="legend-icon series-cluster"></span> Series Clusters &nbsp;
            <span class="legend-icon mega-cluster"></span> Mega Clusters
          </div>
          <div>
            <span class="legend-icon anime-node"></span> Anime &nbsp;
            <span class="legend-icon manga-node"></span> Manga &nbsp;
            <span class="legend-icon other-node"></span> Standalone
          </div>
        </div>
        <div class="instructions">
          <div>Wheel: zoom, Drag: pan</div>
          <div>Double-click clusters to dive in</div>
        </div>
      </div>

      <!-- Controls -->
      <div class="controls-panel">
        <button @click="zoomIn" class="control-button">Zoom In</button>
        <button @click="zoomOut" class="control-button">Zoom Out</button>
        <button @click="resetView" class="control-button">Reset</button>
        <button @click="goToOverview" class="control-button">Overview</button>
        <button v-if="currentCluster" @click="goBack" class="control-button back-button">
          ← Back
        </button>
      </div>

      <!-- Breadcrumb -->
      <div v-if="breadcrumb.length > 0" class="breadcrumb">
        <span
          v-for="(crumb, index) in breadcrumb"
          :key="index"
          @click="navigateToBreadcrumb(index)"
          class="breadcrumb-item"
        >
          {{ crumb.name }}
          <span v-if="index < breadcrumb.length - 1" class="breadcrumb-separator">→</span>
        </span>
      </div>

      <!-- Node Info Tooltip -->
      <div
        v-if="hoveredElement"
        :style="{ left: tooltipPos.x + 'px', top: tooltipPos.y + 'px' }"
        class="tooltip"
      >
        <div class="tooltip-title">
          {{
            hoveredElement.name ||
            hoveredElement.label ||
            `${hoveredElement.type} ${hoveredElement.id}`
          }}
        </div>
        <div v-if="hoveredElement.isCluster" class="tooltip-item">
          Type: {{ hoveredElement.clusterType }} Cluster
        </div>
        <div v-if="hoveredElement.isCluster" class="tooltip-item">
          Contains: {{ hoveredElement.size }} items
        </div>
        <div v-else class="tooltip-item">Type: {{ hoveredElement.type }}</div>
        <div v-if="!hoveredElement.isCluster" class="tooltip-item">
          Connections: {{ hoveredElement.connectionCount || 0 }}
        </div>
        <div v-if="hoveredElement.year" class="tooltip-item">Year: {{ hoveredElement.year }}</div>
        <div v-if="hoveredElement.score" class="tooltip-item">
          Score: {{ hoveredElement.score }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed } from 'vue'
import axios from 'axios'
import * as d3 from 'd3'

// Reactive state

const loading = ref(true)
const error = ref(null)
const progressText = ref('')
const rawNodes = ref([])
const rawLinks = ref([])
const clusters = ref(new Map())
const visibleElements = ref([])
const totalNodes = ref(0)
const totalClusters = ref(0)
const zoomLevel = ref(1)
const searchTerm = ref('')
const searchResults = ref([])
const hoveredElement = ref(null)
const tooltipPos = ref({ x: 0, y: 0 })
const currentCluster = ref(null)
const currentViewLevel = ref('Overview')
const breadcrumb = ref([])
function getTypeColor(type) {
  const colors = {
    anime: '#3b82f6',
    manga: '#ec4899',
    other: '#10b981',
  }
  return colors[type] || '#6b7280'
}
// Computed properties to prevent reactive mutations

const svgDimensions = computed(() => ({
  width: 2400,
  height: 1600,
}))

const visibleElementsCount = computed(() => visibleElements.value.length)

// Refs / graph state - Fixed references

const svgRef = ref(null)
const minimapRef = ref(null)

// Non-reactive D3 variables to prevent recursive updates
let svg, container, zoom, simulation
let nodeMap = new Map()
let latestSeriesClusters = []

// Constants

const VIEW_LEVELS = {
  OVERVIEW: 'Overview',
  MEGA_CLUSTER: 'Mega Cluster',
  SERIES_CLUSTER: 'Series Cluster',
}

const STANDALONE_GROUP_SIZE = 300
const MEGA_CLUSTER_THRESHOLD = 150
const MEGA_CLUSTER_SIZE = 12
const MAX_ITEMS_VISIBLE_IN_CLUSTER = 1500

//Web Worker (inline)
function createClusterWorker() {
  const workerCode = `
    onmessage = (e) => {
      const { nodes, links, standaloneGroupSize, megaThreshold, megaSize } = e.data

      // Build adjacency list
      const adjacency = new Map()
      nodes.forEach(n => adjacency.set(n.id, new Set()))
      for (const link of links) {
        const s = typeof link.source === 'object' ? link.source.id : link.source
        const t = typeof link.target === 'object' ? link.target.id : link.target
        if (adjacency.has(s) && adjacency.has(t)) {
          adjacency.get(s).add(t)
          adjacency.get(t).add(s)
        }
      }

      const visited = new Set()
      const idToNode = new Map(nodes.map(n => [n.id, n]))
      const seriesClusters = []
      const standaloneItems = []
      const queue = []

      let processed = 0
      const total = nodes.length

      // Helper function to extract clean series name
      function extractSeriesName(title) {
        if (!title) return null

        // Remove common patterns that indicate sequels/seasons/parts
        let cleanTitle = title
          .replace(/\\s*(Season|Series|Part|Vol\\.?|Volume|Chapter|Episode|OVA|ONA|Movie|Film)\\s*\\d+.*$/i, '')
          .replace(/\\s*(II+|2nd|3rd|4th|5th|\\d+st|\\d+nd|\\d+rd|\\d+th).*$/i, '')
          .replace(/\\s*\\d+.*$/, '')
          .replace(/\\s*[:：-].*$/, '') // Remove subtitles after colon/dash
          .replace(/\\s*\\(.*\\).*$/, '') // Remove parenthetical content
          .replace(/\\s*\\[.*\\].*$/, '') // Remove bracketed content
          .trim()

        // If we removed everything, use original
        if (!cleanTitle) cleanTitle = title

        return cleanTitle
      }

      // Helper to find best representative name for a cluster
      function getBestClusterName(component) {
        if (component.length === 0) return 'Unknown'
        if (component.length === 1) return component[0].label || component[0].name || 'Single Item'

        // Count occurrences of each clean series name
        const nameCount = new Map()
        const degreeMap = new Map()

        component.forEach(node => {
          const degree = adjacency.get(node.id)?.size || 0
          degreeMap.set(node.id, degree)

          const rawName = node.label || node.name || ''
          const cleanName = extractSeriesName(rawName)
          if (cleanName && cleanName.length > 2) { // Ignore very short names
            nameCount.set(cleanName, (nameCount.get(cleanName) || 0) + 1)
          }
        })

        // If we have recurring clean names, use the most common one
        if (nameCount.size > 0) {
          const sortedNames = Array.from(nameCount.entries())
            .sort((a, b) => b[1] - a[1]) // Sort by count descending

          if (sortedNames[0][1] > 1) { // If most common name appears more than once
            return sortedNames[0][0]
          }
        }

        // Fallback: use the name of the most connected node
        let mostConnected = component[0]
        let maxDegree = degreeMap.get(mostConnected.id) || 0

        component.forEach(node => {
          const degree = degreeMap.get(node.id) || 0
          if (degree > maxDegree) {
            maxDegree = degree
            mostConnected = node
          }
        })

        const bestName = mostConnected.label || mostConnected.name || 'Unknown'
        return extractSeriesName(bestName) || bestName
      }

      // Helper function to check if two titles are related
      function areTitlesRelated(title1, title2) {
        if (!title1 || !title2) return false

        // Clean and normalize titles
        const clean1 = title1.toLowerCase().replace(/[^a-z0-9]/g, '')
        const clean2 = title2.toLowerCase().replace(/[^a-z0-9]/g, '')

        // Check if one title contains the other
        if (clean1.includes(clean2) || clean2.includes(clean1)) return true

        // Calculate similarity (you can adjust the threshold)
        let similarity = 0
        const shorter = clean1.length < clean2.length ? clean1 : clean2
        const longer = clean1.length < clean2.length ? clean2 : clean1

        for (let i = 0; i < shorter.length; i++) {
          if (shorter[i] === longer[i]) similarity++
        }

        return similarity / longer.length > 0.7
      }

      // Find connected components using BFS
      for (const node of nodes) {
        if (visited.has(node.id)) {
          processed++;
          if (processed % 1000 === 0) {
            postMessage({ type: 'progress', text: 'Clustering components ' + processed + '/' + total })
          }
          continue
        }

        // BFS to find connected component
        const component = []
        queue.length = 0
        queue.push(node.id)

        while (queue.length) {
          const nodeId = queue.shift()
          if (visited.has(nodeId)) continue

          visited.add(nodeId)
          const currentNode = idToNode.get(nodeId)
          if (!currentNode) continue

          // Only add to component if title is related to existing nodes
          if (component.length === 0 ||
              component.some(node => areTitlesRelated(
                node.label || node.name,
                currentNode.label || currentNode.name
              ))) {
            component.push(currentNode)
          }

          const neighbors = adjacency.get(nodeId)
          if (neighbors) {
            for (const neighborId of neighbors) {
              if (!visited.has(neighborId)) {
                const neighborNode = idToNode.get(neighborId)
                if (neighborNode && areTitlesRelated(
                  currentNode.label || currentNode.name,
                  neighborNode.label || neighborNode.name
                )) {
                  queue.push(neighborId)
                }
              }
            }
          }
        }

        // Categorize the component
        const componentSize = component.length
        const totalConnections = component.reduce((sum, n) => sum + (adjacency.get(n.id)?.size || 0), 0)

        if (componentSize === 1 && totalConnections === 0) {
          // Truly isolated node
          standaloneItems.push(component[0])
        } else if (componentSize < 3 && totalConnections < 4) {
          // Very small weakly connected component - treat as standalone
          standaloneItems.push(...component)
        } else {
          // Create a proper series cluster
          const clusterName = getBestClusterName(component)

          seriesClusters.push({
            id: 'series_cluster_' + seriesClusters.length,
            name: clusterName,
            itemIds: component.map(x => x.id),
            size: componentSize,
            clusterType: 'series',
            isCluster: true,
            connectionDensity: totalConnections / (componentSize * (componentSize - 1) || 1)
          })
        }

        processed++
        if (processed % 1000 === 0) {
          postMessage({ type: 'progress', text: 'Clustering components ' + processed + '/' + total })
        }
      }

      // Group standalone items
      if (standaloneItems.length > 0) {
        const totalStandaloneItems = standaloneItems.length;
        const standaloneClusterName = "Big Chungus";
        seriesClusters.push({
          id: 'bigChungus',
          name: standaloneClusterName,
          itemIds: standaloneItems.map((item) => item.id),
          size: totalStandaloneItems,
          clusterType: 'mega',
          isCluster: true,
          connectionDensity: 0,
        });
}

      // Create mega clusters if there are too many series clusters
      // Filter out standalone clusters before mega-clustering
      const seriesClustersOnly = seriesClusters.filter(c => c.clusterType !== 'standalone' && c.size <= 10);

      let finalClusters = seriesClusters;
      if (seriesClustersOnly.length > megaThreshold) {
        // Sort clusters by size (largest first)
        seriesClustersOnly.sort((a, b) => b.size - a.size);

        const megaClusters = [];
        for (let i = 0; i < seriesClustersOnly.length; i += megaSize) {
          const chunk = seriesClustersOnly.slice(i, i + megaSize);
          const totalItems = chunk.reduce((sum, c) => sum + c.size, 0);
          const avgSize = Math.round(totalItems / chunk.length);

          const topClusters = chunk
            .filter(c => c.size > avgSize * 0.5)
            .slice(0, 3)
            .map(c => c.name);

          const megaName = topClusters.length > 0
            ? topClusters.slice(0, 2).join(' & ') + (topClusters.length > 2 ? ' +' + (chunk.length - 2) : '')
            : 'Mixed Series Group ' + (Math.floor(i / megaSize) + 1);

          megaClusters.push({
            id: 'mega_cluster_' + Math.floor(i / megaSize),
            name: megaName,
            clusters: chunk.map(c => ({
              id: c.id,
              name: c.name,
              size: c.size,
              clusterType: c.clusterType,
              isCluster: true,
              itemIds: c.itemIds,
              connectionDensity: c.connectionDensity
            })),
            size: totalItems,
            clusterType: 'mega',
            isCluster: true,
            connectionDensity: chunk.reduce((sum, c) => sum + (c.connectionDensity || 0), 0) / chunk.length
          });
        }

        // Merge mega clusters with standalone clusters (if you want to show them too)
        finalClusters = [
          ...megaClusters,
          ...seriesClusters.filter(c => c.clusterType === 'standalone' || c.size > 10)
        ];
      }


      postMessage({
        type: 'done',
        clusters: finalClusters,
        seriesClusters,
        megaUsed: seriesClusters.length > megaThreshold,
        stats: {
          totalComponents: seriesClusters.length,
          standaloneCount: standaloneItems.length,
          largestCluster: Math.max(...seriesClusters.map(c => c.size), 0)
        }
      })
    }
  `
  const blob = new Blob([workerCode], { type: 'application/javascript' })
  return new Worker(URL.createObjectURL(blob))
}

// Rendering helpers

const getElementColor = (element) => {
  if (element.isCluster) {
    switch (element.clusterType) {
      case 'series':
        return '#3B82F6'
      case 'mega':
        return '#10B981'
      case 'standalone':
        return '#6B7280'
      default:
        return '#8B5CF6'
    }
  } else {
    switch (element.type) {
      case 'anime':
        return '#3B82F6'
      case 'manga':
        return '#EC4899'
      default:
        return '#10B981'
    }
  }
}

const getElementStrokeColor = (element) => {
  if (element.isCluster) {
    switch (element.clusterType) {
      case 'series':
        return '#1E40AF'
      case 'mega':
        return '#047857'
      case 'standalone':
        return '#374151'
      default:
        return '#5B21B6'
    }
  } else {
    switch (element.type) {
      case 'anime':
        return '#1E40AF'
      case 'manga':
        return '#BE185D'
      default:
        return '#047857'
    }
  }
}

//D3 rendering

function setupSVG() {
  const svgEl = svgRef.value
  if (!svgEl) {
    console.error('SVG element not found! svgRef.value is:', svgRef.value)
    console.error('DOM ready state:', document.readyState)
    return false
  }

  console.log(`Setting up SVG: ${svgDimensions.value.width}x${svgDimensions.value.height}`)
  console.log('SVG element:', svgEl)

  svg = d3.select(svgEl)
  svg.selectAll('*').remove()
  container = svg.append('g').attr('class', 'main-container')

  const defs = svg.append('defs')

  const colors = [
    { name: '3B82F6', light: '#60A5FA', dark: '#1E40AF' },
    { name: 'EC4899', light: '#F472B6', dark: '#BE185D' },
    { name: '10B981', light: '#34D399', dark: '#047857' },
    { name: '8B5CF6', light: '#A78BFA', dark: '#5B21B6' },
    { name: '6B7280', light: '#9CA3AF', dark: '#374151' },
  ]

  colors.forEach((color) => {
    const radialGrad = defs
      .append('radialGradient')
      .attr('id', `radial-gradient-${color.name}`)
      .attr('cx', '30%')
      .attr('cy', '30%')
      .attr('r', '70%')

    radialGrad
      .append('stop')
      .attr('offset', '0%')
      .attr('stop-color', color.light)
      .attr('stop-opacity', 1)

    radialGrad
      .append('stop')
      .attr('offset', '70%')
      .attr('stop-color', `#${color.name}`)
      .attr('stop-opacity', 0.8)

    radialGrad
      .append('stop')
      .attr('offset', '100%')
      .attr('stop-color', color.dark)
      .attr('stop-opacity', 0.6)

    const glowGrad = defs
      .append('radialGradient')
      .attr('id', `glow-gradient-${color.name}`)
      .attr('cx', '50%')
      .attr('cy', '50%')
      .attr('r', '50%')

    glowGrad
      .append('stop')
      .attr('offset', '0%')
      .attr('stop-color', color.light)
      .attr('stop-opacity', 0.6)

    glowGrad
      .append('stop')
      .attr('offset', '100%')
      .attr('stop-color', `#${color.name}`)
      .attr('stop-opacity', 0)
  })

  const nebulaGrad = defs
    .append('radialGradient')
    .attr('id', 'nebula-gradient')
    .attr('cx', '50%')
    .attr('cy', '50%')
    .attr('r', '50%')

  nebulaGrad
    .append('stop')
    .attr('offset', '0%')
    .attr('stop-color', '#8B5CF6')
    .attr('stop-opacity', 0.3)

  nebulaGrad
    .append('stop')
    .attr('offset', '50%')
    .attr('stop-color', '#3B82F6')
    .attr('stop-opacity', 0.2)

  nebulaGrad
    .append('stop')
    .attr('offset', '100%')
    .attr('stop-color', '#1E1B4B')
    .attr('stop-opacity', 0)

  const glowFilter = defs
    .append('filter')
    .attr('id', 'glow')
    .attr('x', '-50%')
    .attr('y', '-50%')
    .attr('width', '200%')
    .attr('height', '200%')

  glowFilter.append('feGaussianBlur').attr('stdDeviation', '3').attr('result', 'coloredBlur')

  const feMerge = glowFilter.append('feMerge')
  feMerge.append('feMergeNode').attr('in', 'coloredBlur')
  feMerge.append('feMergeNode').attr('in', 'SourceGraphic')

  zoom = d3
    .zoom()
    .scaleExtent([0.1, 10])
    .on('zoom', (event) => {
      const { transform } = event
      container.attr('transform', transform)
      zoomLevel.value = transform.k
    })
  svg.call(zoom)

  return true
}

function addParticleEffect(element, container) {
  if (!element.isCluster || element.size < 50) return

  const particles = container.append('g').attr('class', 'particles')

  for (let i = 0; i < Math.min(element.size / 10, 15); i++) {
    const angle = (i / 15) * Math.PI * 2
    const distance = 30 + Math.random() * 40

    particles
      .append('circle')
      .attr('cx', element.x + Math.cos(angle) * distance)
      .attr('cy', element.y + Math.sin(angle) * distance)
      .attr('r', 0.5 + Math.random() * 1.5)
      .attr('fill', '#60a5fa')
      .attr('opacity', 0.7)
      .transition()
      .duration(2000 + Math.random() * 3000)
      .ease(d3.easeLinear)
      .attr('transform', `rotate(${360} ${element.x} ${element.y})`)
      .attr('opacity', 0.2)
      .on('end', function () {
        d3.select(this).remove()
      })
  }
}

function renderMinimap() {
  if (!minimapRef.value || visibleElements.value.length === 0) return
  const minimap = d3.select(minimapRef.value)
  minimap.selectAll('*').remove()

  minimap
    .append('rect')
    .attr('width', '100%')
    .attr('height', '100%')
    .attr('fill', '#0f0f23')
    .attr('stroke', '#374151')
    .attr('stroke-width', 1)

  const scaleX = d3.scaleLinear().domain([0, svgDimensions.value.width]).range([5, 145])
  const scaleY = d3.scaleLinear().domain([0, svgDimensions.value.height]).range([5, 95])
  const sampleElements = visibleElements.value.filter((_, i) => i % 3 === 0)

  minimap
    .selectAll('.mini-element')
    .data(sampleElements)
    .enter()
    .append('circle')
    .attr('class', 'mini-element')
    .attr('cx', (d) => scaleX(d.x || svgDimensions.value.width / 2))
    .attr('cy', (d) => scaleY(d.y || svgDimensions.value.height / 2))
    .attr('r', (d) => (d.isCluster ? 3 : 1.5))
    .attr('fill', (d) => getElementColor(d))
    .attr('opacity', 0.8)
    .attr('filter', 'url(#glow)')
}

function renderElements(elements, elementType, links = []) {
  if (!container || elements.length === 0) return

  container.selectAll('*').remove()
  if (simulation) {
    simulation.stop()
    simulation = null
  }

  // Create local copies to avoid reactive mutations
  const elemsCopy = elements.map((d) => ({
    ...d,
    x: d.x || svgDimensions.value.width / 2 + (Math.random() - 0.5) * 100,
    y: d.y || svgDimensions.value.height / 2 + (Math.random() - 0.5) * 100,
  }))

  // Create node lookup map for link references
  const nodeById = new Map(elemsCopy.map((node) => [node.id, node]))

  // Process links
  const processedLinks = links
    .map((link) => {
      const sourceId = typeof link.source === 'object' ? link.source.id : link.source
      const targetId = typeof link.target === 'object' ? link.target.id : link.target
      const source = nodeById.get(sourceId)
      const target = nodeById.get(targetId)
      return source && target ? { source, target } : null
    })
    .filter(Boolean)

  // Create simulation
  simulation = d3
    .forceSimulation(elemsCopy)
    .force('charge', d3.forceManyBody().strength(-200))
    .force(
      'center',
      d3.forceCenter(svgDimensions.value.width / 2, svgDimensions.value.height / 2).strength(0.1),
    )
    .force(
      'collision',
      d3
        .forceCollide()
        .radius((d) => Math.max(25, Math.sqrt(d.size || 1) * 6))
        .strength(0.8),
    )
    .force('link', d3.forceLink(processedLinks).distance(150).strength(0.5))

  // Add link force if we have links
  if (processedLinks.length > 0) {
    simulation.force(
      'link',
      d3
        .forceLink(processedLinks)
        .id((d) => d.id)
        .distance(80)
        .strength(0.8),
    )

    // Create enhanced links
    const linkGroups = container
      .append('g')
      .attr('class', 'links')
      .selectAll('.link-group')
      .data(processedLinks)
      .join('g')
      .attr('class', 'link-group')

    // Base connection line
    linkGroups
      .append('line')
      .attr('class', 'link-base')
      .attr('stroke', '#1e40af')
      .attr('stroke-width', 2)
      .attr('stroke-opacity', 0.3)

    // Energy flow line
    linkGroups
      .append('line')
      .attr('class', 'link-energy')
      .attr('stroke', '#60a5fa')
      .attr('stroke-width', 1)
      .attr('stroke-opacity', 0.8)
      .style('filter', 'url(#glow)')
      .attr('stroke-dasharray', '4,4')
      .style('animation', 'energy-flow 3s linear infinite')

    linkGroups
      .filter((d) => (d.weight || 1) > 2)
      .append('line')
      .attr('class', 'link-pulse')
      .attr('stroke', '#a78bfa')
      .attr('stroke-width', 3)
      .attr('stroke-opacity', 0)
      .style('animation', 'connection-pulse 2s ease-in-out infinite')
  }

  const elementGroups = container
    .append('g')
    .attr('class', 'nodes')
    .selectAll('.element')
    .data(elemsCopy)
    .join('g')
    .attr('class', 'element')
    .style('cursor', 'pointer')
    .call(d3.drag().on('start', dragstarted).on('drag', dragged).on('end', dragended))
    .on('mouseover', handleElementMouseover)
    .on('mouseout', handleElementMouseout)
    .on('click', handleElementClick)
    .on('dblclick', handleElementDoubleClick)

  elementGroups
    .filter((d) => d.clusterType === 'mega')
    .insert('ellipse', ':first-child')
    .attr('class', 'nebula-background')
    .attr('rx', (d) => Math.min(80, Math.max(40, Math.sqrt(d.size || 1) * 8)))
    .attr('ry', (d) => Math.min(60, Math.max(30, Math.sqrt(d.size || 1) * 6)))
    .attr('fill', 'url(#nebula-gradient)')
    .attr('opacity', 0.3)

  elementGroups
    .append('circle')
    .attr('class', 'node-glow')
    .attr('r', (d) => {
      if (elementType === 'cluster') {
        const baseRadius = 25
        const sizeRadius = Math.sqrt(d.size || 1) * 4
        const maxRadius = 75
        return Math.min(maxRadius, Math.max(baseRadius, sizeRadius)) + 12
      } else {
        return 20
      }
    })
    .attr('fill', (d) => {
      const color = getElementColor(d).substring(1)
      return `url(#glow-gradient-${color})`
    })
    .attr('opacity', 0.4)

  elementGroups
    .filter((d) => d.id === 'bigChungus')
    .style('cursor', 'not-allowed')
    .style('opacity', 0.7)
    .append('text')
    .attr('class', 'non-interactive-label')
    .attr('text-anchor', 'middle')
    .attr('dy', -40)
    .attr('fill', '#9ca3af')
    .attr('font-size', '12px')
    .attr('font-weight', 'bold')
    .style('pointer-events', 'none')
    .text('70k+ items - view only')

  function getHexagonPoints(radius) {
    const points = []
    for (let i = 0; i < 6; i++) {
      const angle = (i * Math.PI) / 3
      const x = radius * Math.cos(angle)
      const y = radius * Math.sin(angle)
      points.push(`${x},${y}`)
    }
    return points.join(' ')
  }

  elementGroups
    .filter((d) => d.isCluster)
    .append('polygon')
    .attr('class', 'node-hexagon')
    .attr('points', (d) => {
      const baseRadius = 25
      const sizeRadius = Math.sqrt(d.size || 1) * 4
      const maxRadius = 75
      const radius = Math.min(maxRadius, Math.max(baseRadius, sizeRadius))
      return getHexagonPoints(radius)
    })
    .attr('fill', (d) => {
      const color = getElementColor(d).substring(1)
      return `url(#radial-gradient-${color})`
    })
    .attr('stroke', (d) => getElementStrokeColor(d))
    .attr('stroke-width', 3)
    .attr('filter', 'url(#glow)')

  elementGroups
    .filter((d) => !d.isCluster && d.type === 'anime')
    .append('rect')
    .attr('class', 'node-anime')
    .attr('width', 20)
    .attr('height', 20)
    .attr('x', -10)
    .attr('y', -10)
    .attr('rx', 4)
    .attr('fill', (d) => {
      const color = getElementColor(d).substring(1)
      return `url(#radial-gradient-${color})`
    })
    .attr('stroke', (d) => getElementStrokeColor(d))
    .attr('stroke-width', 2)
    .attr('filter', 'url(#glow)')

  elementGroups
    .filter((d) => !d.isCluster && d.type === 'manga')
    .append('path')
    .attr('class', 'node-manga')
    .attr('d', 'M0,-15 L13,0 L0,15 L-13,0 Z')
    .attr('fill', (d) => {
      const color = getElementColor(d).substring(1)
      return `url(#radial-gradient-${color})`
    })
    .attr('stroke', (d) => getElementStrokeColor(d))
    .attr('stroke-width', 2)
    .attr('filter', 'url(#glow)')

  elementGroups
    .filter((d) => !d.isCluster && d.type === 'other')
    .append('circle')
    .attr('class', 'node-other')
    .attr('r', 12)
    .attr('fill', (d) => {
      const color = getElementColor(d).substring(1)
      return `url(#radial-gradient-${color})`
    })
    .attr('stroke', (d) => getElementStrokeColor(d))
    .attr('stroke-width', 2)
    .attr('filter', 'url(#glow)')
    .attr('fill', (d) => {
      const color = getElementColor(d).substring(1)
      return `url(#radial-gradient-${color})`
    })
    .attr('stroke', (d) => getElementStrokeColor(d))
    .attr('stroke-width', 2)
    .attr('filter', 'url(#glow)')

  elementGroups
    .filter((d) => d.isCluster)
    .append('circle')
    .attr('class', 'node-sparkle')
    .attr('r', 3)
    .attr('fill', '#ffffff')
    .attr('opacity', 0.8)
    .attr('cx', -5)
    .attr('cy', -5)

  elementGroups
    .append('text')
    .attr('class', 'element-label')
    .attr('text-anchor', 'middle')
    .attr('dy', (d) => {
      if (elementType === 'cluster') {
        const baseRadius = 25
        const sizeRadius = Math.sqrt(d.size || 1) * 4
        const maxRadius = 75
        const radius = Math.min(maxRadius, Math.max(baseRadius, sizeRadius))
        return radius + 20
      } else {
        return 15 + 20
      }
    })
    .attr('fill', '#E5E7EB')
    .attr('font-size', (d) => {
      if (elementType === 'cluster') {
        const baseSize = Math.max(11, Math.min(16, Math.log(d.size || 1) * 2 + 9))
        return baseSize + 'px'
      } else {
        return '11px'
      }
    })
    .attr('font-weight', elementType === 'cluster' ? 'bold' : 'normal')
    .attr('text-shadow', '2px 2px 4px rgba(0,0,0,0.8)')
    .style('pointer-events', 'none')
    .text((d) => {
      const name = d.name || d.label || `${d.type} ${d.id}`
      const maxLength = elementType === 'cluster' ? (d.size > 100 ? 35 : d.size > 50 ? 30 : 25) : 25
      return name.length > maxLength ? name.substring(0, maxLength - 3) + '...' : name
    })

  // Add composition indicators for large clusters
  elementGroups
    .filter((d) => d.isCluster && d.size > 20)
    .append('g')
    .attr('class', 'cluster-composition')
    .each(function (d) {
      const group = d3.select(this)
      const items = d.itemIds ? d.itemIds.map((id) => nodeMap.get(id)).filter(Boolean) : []

      if (items.length === 0) return

      const typeCounts = { anime: 0, manga: 0, other: 0 }
      items.forEach((item) => {
        typeCounts[item.type || 'other']++
      })

      // Create mini pie chart
      const total = items.length
      const data = Object.entries(typeCounts)
        .filter(([type, count]) => count > 0)
        .map(([type, count]) => ({ type, count, percentage: count / total }))

      let currentAngle = 0
      data.forEach(({ type, percentage }, i) => {
        const angle = percentage * 2 * Math.PI
        const startAngle = currentAngle
        const endAngle = currentAngle + angle

        const arc = d3
          .arc()
          .innerRadius(18)
          .outerRadius(25)
          .startAngle(startAngle)
          .endAngle(endAngle)

        group
          .append('path')
          .attr('d', arc)
          .attr('fill', getTypeColor(type))
          .attr('opacity', 0.7)
          .attr('transform', 'translate(25, -25)')
          .append('title')
          .text(`${type}: ${typeCounts[type]} items`)

        currentAngle = endAngle
      })

      // Add size indicator
      group
        .append('text')
        .attr('x', 25)
        .attr('y', 5)
        .attr('text-anchor', 'middle')
        .attr('font-size', '9px')
        .attr('fill', '#e5e7eb')
        .attr('font-weight', 'bold')
        .text(total)
    })

  // Update positions on each tick
  simulation.on('tick', () => {
    // Update all link types
    container
      .selectAll('.link-base, .link-energy, .link-pulse')
      .attr('x1', (d) => d.source.x)
      .attr('y1', (d) => d.source.y)
      .attr('x2', (d) => d.target.x)
      .attr('y2', (d) => d.target.y)

    // Update node positions with subtle rotation based on velocity
    elementGroups.attr('transform', (d) => {
      const rotation = Math.atan2(d.vy || 0, d.vx || 0) * (180 / Math.PI) * 0.1
      return `translate(${d.x},${d.y}) rotate(${rotation})`
    })
  })

  // Add particle effects for large clusters
  setTimeout(() => {
    elemsCopy
      .filter((d) => d.isCluster && d.size > 30)
      .forEach((d) => addParticleEffect(d, container))
  }, 1000)

  simulation.alpha(1).restart()

  // Update visible elements
  nextTick(() => {
    visibleElements.value = elemsCopy
    setTimeout(() => renderMinimap(), 200)
  })
}

// View transitions

function renderOverview() {
  currentCluster.value = null
  currentViewLevel.value = VIEW_LEVELS.OVERVIEW
  renderClusters(Array.from(clusters.value.values()))
}

function renderClusters(clusterArray) {
  console.log(`Rendering ${clusterArray.length} clusters as star system`)

  // Sort clusters by size
  const sortedClusters = [...clusterArray].sort((a, b) => b.size - a.size)

  // Separate Big Chungus and other clusters
  const bigChungus = sortedClusters.find((c) => c.id === 'bigChungus')
  const otherClusters = sortedClusters.filter((c) => c.id !== 'bigChungus')

  // Calculate dimensions
  const centerX = svgDimensions.value.width / 2
  const centerY = svgDimensions.value.height / 2
  const maxOrbitRadius = Math.min(centerX, centerY) * 0.8

  // Position Big Chungus in the center
  if (bigChungus) {
    bigChungus.x = centerX
    bigChungus.y = centerY
    bigChungus.fixed = true
  }

  // Create orbiting rings based on cluster sizes
  const orbits = []
  let currentRadius = 150

  // Group clusters by size ranges
  const sizeGroups = {}
  otherClusters.forEach((cluster) => {
    const sizeKey = Math.floor(Math.log2(cluster.size))
    if (!sizeGroups[sizeKey]) sizeGroups[sizeKey] = []
    sizeGroups[sizeKey].push(cluster)
  })

  // Create orbits from size groups
  Object.entries(sizeGroups)
    .sort((a, b) => Number(b[0]) - Number(a[0])) // Larger clusters in inner orbits
    .forEach(([sizeKey, clusters]) => {
      orbits.push({
        radius: currentRadius,
        clusters: clusters,
      })
      currentRadius += 120 + Math.random() * 50 // Add some randomness to orbit spacing
    })

  // Position clusters in their orbits
  orbits.forEach((orbit) => {
    const clusterCount = orbit.clusters.length
    orbit.clusters.forEach((cluster, i) => {
      const baseAngle = (i / clusterCount) * 2 * Math.PI

      const angleOffset = (Math.random() - 0.5) * 0.2
      const radiusOffset = (Math.random() - 0.5) * 20

      const angle = baseAngle + angleOffset
      const radius = orbit.radius + radiusOffset

      cluster.x = centerX + Math.cos(angle) * radius
      cluster.y = centerY + Math.sin(angle) * radius

      cluster.orbitRadius = radius
      cluster.orbitAngle = angle
      cluster.orbitSpeed = 0.001 / Math.sqrt(radius)
    })
  })

  if (simulation) simulation.stop()

  simulation = d3
    .forceSimulation([bigChungus, ...otherClusters])
    .force(
      'collision',
      d3.forceCollide().radius((d) => Math.sqrt(d.size) * 2),
    )
    .force('orbit', (alpha) => {
      otherClusters.forEach((cluster) => {
        if (!cluster.orbitAngle) return

        cluster.orbitAngle += cluster.orbitSpeed
        const targetX = centerX + Math.cos(cluster.orbitAngle) * cluster.orbitRadius
        const targetY = centerY + Math.sin(cluster.orbitAngle) * cluster.orbitRadius

        cluster.vx = (targetX - cluster.x) * alpha
        cluster.vy = (targetY - cluster.y) * alpha
      })
    })
    .force('center', d3.forceCenter(centerX, centerY).strength(0.01))

  if (bigChungus) {
    const solarFlareCount = 24
    for (let i = 0; i < solarFlareCount; i++) {
      const angle = (i / solarFlareCount) * Math.PI * 2
      const flareLength = 40 + Math.random() * 30

      container
        .append('path')
        .attr('class', 'solar-flare')
        .attr(
          'd',
          `M ${centerX} ${centerY} l ${Math.cos(angle) * flareLength} ${Math.sin(angle) * flareLength}`,
        )
        .attr('stroke', '#FDB813')
        .attr('stroke-width', 2)
        .attr('opacity', 0.4)
        .style('filter', 'url(#glow)')
    }
  }

  renderElements([bigChungus, ...otherClusters], 'cluster')
}

function renderClusterDetail(cluster) {
  console.log('Rendering cluster:', cluster)
  let items = []

  if (cluster.clusterType === 'mega' && cluster.clusters) {
    items = cluster.clusters.flatMap((subCluster) => {
      if (subCluster.itemIds) {
        return subCluster.itemIds.map((id) => nodeMap.get(id)).filter(Boolean)
      }
      return []
    })
  } else {
    if (cluster.items && cluster.items.length > 0) {
      items = cluster.items.filter((item) => item && item.id)
    } else if (cluster.itemIds && cluster.itemIds.length > 0) {
      items = cluster.itemIds.map((id) => nodeMap.get(id)).filter(Boolean)
    }
  }

  console.log(`Found ${items.length} items in cluster`)

  const validItemsMap = new Map(items.map((item) => [item.id, item]))

  const relevantLinks = rawLinks.value
    .filter((link) => {
      const sourceId = typeof link.source === 'object' ? link.source.id : link.source
      const targetId = typeof link.target === 'object' ? link.target.id : link.target
      return validItemsMap.has(sourceId) && validItemsMap.has(targetId)
    })
    .map((link) => {
      const sourceId = typeof link.source === 'object' ? link.source.id : link.source
      const targetId = typeof link.target === 'object' ? link.target.id : link.target
      return {
        source: sourceId,
        target: targetId,
      }
    })

  currentCluster.value = cluster
  currentViewLevel.value =
    cluster.clusterType === 'mega' ? VIEW_LEVELS.MEGA_CLUSTER : VIEW_LEVELS.SERIES_CLUSTER

  console.log(`Rendering cluster with ${items.length} nodes and ${relevantLinks.length} links`)
  renderElements(items, 'node', relevantLinks)
}

// Events / interactions

function handleElementMouseover(event, d) {
  hoveredElement.value = d
  tooltipPos.value = { x: event.pageX + 10, y: event.pageY - 10 }

  const group = d3.select(event.currentTarget)

  // Add pulsing ring effect
  group
    .append('circle')
    .attr('class', 'hover-ring')
    .attr('r', 25)
    .attr('fill', 'none')
    .attr('stroke', getElementColor(d))
    .attr('stroke-width', 3)
    .attr('opacity', 0.8)
    .transition()
    .duration(1000)
    .attr('r', 60)
    .attr('opacity', 0)
    .on('end', function () {
      d3.select(this).remove()
    })

  // Enhanced hover effect for the main shape
  group
    .selectAll('.node-hexagon, .node-anime, .node-manga, .node-other, .node-core')
    .transition()
    .duration(200)
    .attr('transform', 'scale(1.2)')
    .style('filter', 'url(#glow) brightness(1.4)')

  group
    .select('.node-glow')
    .transition()
    .duration(200)
    .attr('opacity', 0.9)
    .attr('transform', 'scale(1.3)')

  // Highlight connected elements if not in overview
  if (currentViewLevel.value !== VIEW_LEVELS.OVERVIEW) {
    highlightConnectedElements(d.id)
  }
}
function highlightConnectedElements(nodeId) {
  const connectedIds = new Set()

  // Find all connected node IDs
  rawLinks.value.forEach((link) => {
    const sourceId = typeof link.source === 'object' ? link.source.id : link.source
    const targetId = typeof link.target === 'object' ? link.target.id : link.target

    if (sourceId === nodeId) connectedIds.add(targetId)
    if (targetId === nodeId) connectedIds.add(sourceId)
  })

  // Dim unconnected elements
  container
    .selectAll('.element')
    .transition()
    .duration(300)
    .style('opacity', (d) => (connectedIds.has(d.id) || d.id === nodeId ? 1 : 0.2))
    .style('filter', (d) =>
      connectedIds.has(d.id) || d.id === nodeId ? 'brightness(1.3)' : 'brightness(0.6)',
    )

  // Highlight connected links
  container
    .selectAll('.link-group')
    .transition()
    .duration(300)
    .style('opacity', (d) => {
      const sourceId = typeof d.source === 'object' ? d.source.id : d.source
      const targetId = typeof d.target === 'object' ? d.target.id : d.target
      return sourceId === nodeId || targetId === nodeId ? 1 : 0.1
    })
}
function handleElementMouseout(event, d) {
  hoveredElement.value = null

  const group = d3.select(event.currentTarget)

  // Reset hover effects
  group
    .selectAll('.node-hexagon, .node-anime, .node-manga, .node-other, .node-core')
    .transition()
    .duration(200)
    .attr('transform', 'scale(1)')
    .style('filter', 'url(#glow)')

  group
    .select('.node-glow')
    .transition()
    .duration(200)
    .attr('opacity', 0.4)
    .attr('transform', 'scale(1)')

  // Reset all elements opacity
  container
    .selectAll('.element')
    .transition()
    .duration(300)
    .style('opacity', 1)
    .style('filter', 'brightness(1)')

  container.selectAll('.link-group').transition().duration(300).style('opacity', 1)
}
function handleElementClick(event, d) {
  if (d.id === 'bigChungus') {
    console.log('Big Chungus is not interactive due to size (70k+ items)')
    return
  }
  console.log('Element clicked:', d)
}
function handleElementDoubleClick(event, d) {
  // Prevent interaction with Big Chungus due to performance
  if (d.id === 'bigChungus') {
    console.log('Big Chungus contains too many items (70k+) to render effectively')
    return
  }

  if (d.isCluster) {
    if (d.clusterType === 'mega' && d.clusters) {
      breadcrumb.value.push({
        name: d.name,
        cluster: d,
        level: VIEW_LEVELS.MEGA_CLUSTER,
      })
    } else {
      breadcrumb.value.push({
        name: d.name,
        cluster: d,
        level: currentViewLevel.value,
      })
    }
    renderClusterDetail(d)
    resetView()
  }
}
function dragstarted(event, d) {
  if (!event.active && simulation) simulation.alphaTarget(0.3).restart()
  d.fx = d.x
  d.fy = d.y
}

function dragged(event, d) {
  d.fx = event.x
  d.fy = event.y
}

function dragended(event, d) {
  if (!event.active && simulation) simulation.alphaTarget(0)
  d.fx = null
  d.fy = null
}

//Navigation

function goBack() {
  if (breadcrumb.value.length > 0) {
    breadcrumb.value.pop()
    if (breadcrumb.value.length === 0) {
      renderOverview()
    } else {
      const previous = breadcrumb.value[breadcrumb.value.length - 1]
      renderClusterDetail(previous.cluster)
    }
    resetView()
  }
}

function goToOverview() {
  breadcrumb.value = []
  renderOverview()
  resetView()
}

function navigateToBreadcrumb(index) {
  breadcrumb.value = breadcrumb.value.slice(0, index + 1)
  if (index === -1 || breadcrumb.value.length === 0) {
    goToOverview()
  } else {
    const target = breadcrumb.value[index]
    renderClusterDetail(target.cluster)
  }
  resetView()
}

// Search

function handleSearch() {
  if (!searchTerm.value.trim()) {
    searchResults.value = []
    return
  }
  const query = searchTerm.value.toLowerCase()
  searchResults.value = Array.from(nodeMap.values())
    .filter((node) => (node.label || node.name || '').toLowerCase().includes(query))
    .sort((a, b) => {
      const aLabel = (a.label || a.name || '').toLowerCase()
      const bLabel = (b.label || b.name || '').toLowerCase()
      const aExact = aLabel === query,
        bExact = bLabel === query
      if (aExact !== bExact) return bExact - aExact
      const aStarts = aLabel.startsWith(query),
        bStarts = bLabel.startsWith(query)
      if (aStarts !== bStarts) return bStarts - aStarts
      return (b.connectionCount || 0) - (a.connectionCount || 0)
    })
    .slice(0, 20)
}

function focusOnNode(node) {
  searchTerm.value = ''
  searchResults.value = []

  const targetCluster = latestSeriesClusters.find((c) => (c.itemIds || []).includes(node.id))
  if (targetCluster) {
    breadcrumb.value = []
    renderClusterDetail(targetCluster)
    setTimeout(() => {
      const foundNode = visibleElements.value.find((el) => el.id === node.id)
      if (foundNode && typeof foundNode.x === 'number' && typeof foundNode.y === 'number') {
        const centerX = svgDimensions.value.width / 2 - foundNode.x
        const centerY = svgDimensions.value.height / 2 - foundNode.y
        svg
          .transition()
          .duration(750)
          .call(zoom.transform, d3.zoomIdentity.translate(centerX, centerY).scale(2))
      }
    }, 800)
  }
}

// Zoom controls
function zoomIn() {
  if (!svg || !zoom) return
  svg.transition().duration(300).call(zoom.scaleBy, 1.5)
}

function zoomOut() {
  if (!svg || !zoom) return
  svg
    .transition()
    .duration(300)
    .call(zoom.scaleBy, 1 / 1.5)
}

function resetView() {
  if (!svg || !zoom) return
  svg.transition().duration(500).call(zoom.transform, d3.zoomIdentity)
}

function handleMinimapClick(event) {
  if (!minimapRef.value) return
  const rect = minimapRef.value.getBoundingClientRect()
  const clickX = event.clientX - rect.left
  const clickY = event.clientY - rect.top
  const worldX = ((clickX - 5) / 140) * svgDimensions.value.width
  const worldY = ((clickY - 5) / 90) * svgDimensions.value.height
  const centerX = svgDimensions.value.width / 2 - worldX
  const centerY = svgDimensions.value.height / 2 - worldY
  svg
    .transition()
    .duration(500)
    .call(zoom.transform, d3.zoomIdentity.translate(centerX, centerY).scale(zoomLevel.value))
}

// Initialize
async function initializeVisualization(clusterPayload) {
  console.log('Initializing hierarchical visualization...')
  console.log('Clusters received:', clusterPayload.clusters.length)

  await nextTick()
  await nextTick()

  let retries = 0
  while (!svgRef.value && retries < 10) {
    console.log(`Waiting for SVG ref... attempt ${retries + 1}`)
    await new Promise((resolve) => setTimeout(resolve, 100))
    retries++
  }

  if (!svgRef.value) {
    console.error('SVG ref still not available after waiting!')
    error.value = 'SVG element not available'
    return
  }

  if (!setupSVG()) {
    error.value = 'Failed to setup SVG'
    return
  }

  const clusterMap = new Map()
  clusterPayload.clusters.forEach((c) => {
    clusterMap.set(c.id, { ...c })
  })

  clusters.value = clusterMap
  totalClusters.value = clusterMap.size
  latestSeriesClusters = clusterPayload.seriesClusters

  const idToClusterName = new Map()
  clusterPayload.seriesClusters.forEach((c) => {
    c.itemIds.forEach((id) => idToClusterName.set(id, c.name))
  })
  nodeMap.forEach((n, id) => {
    n.clusterName = idToClusterName.get(id) || 'Standalone'
  })

  await nextTick()
  renderOverview()
  console.log('Hierarchical visualization initialized')
}

onMounted(async () => {
  try {
    console.log('Fetching graph data...')
    const res = await axios.get('http://127.0.0.1:8000/graph')

    const nodes = res.data.nodes || []
    const links = Array.isArray(res.data.links)
      ? res.data.links
      : Object.values(res.data.links || {})

    rawNodes.value = nodes
    rawLinks.value = links
    totalNodes.value = nodes.length

    console.log(`Loaded ${nodes.length} nodes and ${links.length} links`)

    const degreeMap = new Map()
    links.forEach((link) => {
      const s = typeof link.source === 'object' ? link.source.id : link.source
      const t = typeof link.target === 'object' ? link.target.id : link.target
      degreeMap.set(s, (degreeMap.get(s) || 0) + 1)
      degreeMap.set(t, (degreeMap.get(t) || 0) + 1)
    })

    nodes.forEach((node) => {
      if (!node.label && !node.name) node.label = `${node.type || 'Item'} ${node.id}`
      if (!node.type) {
        node.type = Math.random() > 0.6 ? 'anime' : Math.random() > 0.5 ? 'manga' : 'other'
      }
      node.connectionCount = degreeMap.get(node.id) || 0
      nodeMap.set(node.id, node)
    })

    const worker = createClusterWorker()
    worker.onmessage = async (msg) => {
      const { type } = msg.data || {}
      if (type === 'progress') {
        progressText.value = msg.data.text
      } else if (type === 'done') {
        progressText.value = ''
        loading.value = false

        await nextTick()
        await nextTick()

        try {
          await initializeVisualization(msg.data)
        } catch (err) {
          console.error('Initialization error:', err)
          error.value = 'Failed to initialize visualization'
        }

        worker.terminate()
      }
    }

    worker.onerror = (err) => {
      console.error('Worker error:', err)
      error.value = 'Clustering failed'
      loading.value = false
    }

    const cleanNodes = JSON.parse(JSON.stringify(nodes))
    const cleanLinks = JSON.parse(JSON.stringify(links))

    worker.postMessage({
      nodes: cleanNodes,
      links: cleanLinks,
      standaloneGroupSize: STANDALONE_GROUP_SIZE,
      megaThreshold: MEGA_CLUSTER_THRESHOLD,
      megaSize: MEGA_CLUSTER_SIZE,
    })
  } catch (err) {
    console.error('Error:', err)
    error.value = 'Failed to load graph data: ' + (err.message || err)
    loading.value = false
  }
})
</script>

<style scoped>
/* Main container */
.clustered-graph-container {
  padding: 24px;
  padding-top: 60px;
  background: radial-gradient(ellipse at center, #0f172a 0%, #020617 70%, #000000 100%);
  min-height: 100vh;
  color: white;
  max-width: 100%;
  margin: 0 auto;
  position: relative;
  overflow: hidden;
}

.clustered-graph-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image:
    radial-gradient(2px 2px at 20px 30px, rgba(255, 255, 255, 0.9), transparent),
    radial-gradient(2px 2px at 40px 70px, rgba(255, 255, 255, 0.7), transparent),
    radial-gradient(1px 1px at 90px 40px, rgba(255, 255, 255, 1), transparent),
    radial-gradient(1px 1px at 130px 80px, rgba(255, 255, 255, 0.6), transparent),
    radial-gradient(2px 2px at 160px 30px, rgba(255, 255, 255, 0.8), transparent),
    radial-gradient(1px 1px at 200px 120px, rgba(255, 255, 255, 0.4), transparent),
    radial-gradient(2px 2px at 300px 60px, rgba(255, 255, 255, 0.9), transparent),
    radial-gradient(1px 1px at 350px 180px, rgba(255, 255, 255, 0.7), transparent);
  background-repeat: repeat;
  background-size: 400px 200px;
  animation: twinkle 6s ease-in-out infinite alternate;
  pointer-events: none;
  z-index: 0;
}

@keyframes twinkle {
  0% {
    opacity: 0.3;
    transform: translateX(0px) translateY(0px);
  }
  25% {
    opacity: 0.8;
  }
  50% {
    opacity: 0.5;
    transform: translateX(2px) translateY(-1px);
  }
  75% {
    opacity: 0.9;
  }
  100% {
    opacity: 0.4;
    transform: translateX(-1px) translateY(1px);
  }
}

.graph-title {
  font-size: 1.8rem;
  font-weight: bold;
  margin-bottom: 20px;
  position: relative;
  z-index: 2;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
  background: linear-gradient(45deg, #60a5fa, #a78bfa, #60a5fa);
  background-size: 200% 200%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: gradient-shift 3s ease-in-out infinite;
}

@keyframes gradient-shift {
  0%,
  100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}

/* Search container */
.search-container {
  margin-bottom: 20px;
  display: flex;
  gap: 16px;
  align-items: center;
  position: relative;
  z-index: 2;
}

.search-input-wrapper {
  position: relative;
  flex: 1;
  max-width: 500px;
}

.search-input {
  width: 100%;
  padding: 12px 20px;
  background: rgba(15, 23, 42, 0.8);
  border: 2px solid rgba(59, 130, 246, 0.3);
  border-radius: 12px;
  color: white;
  outline: none;
  transition: all 0.3s ease;
  font-size: 14px;
  backdrop-filter: blur(10px);
}

.search-input::placeholder {
  color: rgba(156, 163, 175, 0.8);
}

.search-input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
  background: rgba(15, 23, 42, 0.95);
}

.search-results {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: rgba(15, 23, 42, 0.95);
  border: 2px solid rgba(59, 130, 246, 0.3);
  border-top: none;
  border-radius: 0 0 12px 12px;
  max-height: 250px;
  overflow-y: auto;
  z-index: 10;
  backdrop-filter: blur(15px);
}

.search-result-item {
  padding: 12px 20px;
  cursor: pointer;
  border-bottom: 1px solid rgba(75, 85, 99, 0.3);
  transition: all 0.2s ease;
}

.search-result-item:last-child {
  border-bottom: none;
}

.search-result-item:hover {
  background: rgba(59, 130, 246, 0.1);
  transform: translateX(4px);
}

.search-result-title {
  font-weight: 600;
  margin-bottom: 3px;
  color: #e5e7eb;
}

.search-result-subtitle {
  font-size: 0.85rem;
  color: rgba(156, 163, 175, 0.8);
}

/* Loading */
.loading-container {
  text-align: center;
  padding: 60px 40px;
  position: relative;
  z-index: 2;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  margin: 0 auto 20px;
  border: 4px solid rgba(59, 130, 246, 0.2);
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.loading-subtitle {
  font-size: 0.9rem;
  opacity: 0.8;
  margin-top: 10px;
}

/* Graph wrapper */
.graph-wrapper {
  position: relative;
  z-index: 2;
}

.canvas-container {
  position: relative;
  background: radial-gradient(
    ellipse at center,
    rgba(26, 26, 46, 0.8) 0%,
    rgba(22, 33, 62, 0.9) 50%,
    rgba(15, 15, 35, 0.95) 100%
  );
  border-radius: 16px;
  overflow: hidden;
  height: 750px;
  border: 2px solid rgba(59, 130, 246, 0.2);
  backdrop-filter: blur(20px);
  box-shadow:
    0 0 50px rgba(59, 130, 246, 0.1),
    inset 0 0 100px rgba(59, 130, 246, 0.05);
}
.canvas-container::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background:
    radial-gradient(ellipse at 20% 30%, rgba(59, 130, 246, 0.15) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 70%, rgba(167, 139, 250, 0.1) 0%, transparent 50%),
    radial-gradient(ellipse at 40% 80%, rgba(236, 72, 153, 0.08) 0%, transparent 50%),
    radial-gradient(ellipse at 60% 20%, rgba(16, 185, 129, 0.05) 0%, transparent 50%);
  animation: nebula-drift 120s linear infinite;
  pointer-events: none;
  z-index: 1;
}

@keyframes nebula-drift {
  0% {
    transform: translate(0, 0) rotate(0deg) scale(1);
    opacity: 0.3;
  }
  25% {
    opacity: 0.6;
  }
  50% {
    transform: translate(-25%, -25%) rotate(180deg) scale(1.1);
    opacity: 0.4;
  }
  75% {
    opacity: 0.7;
  }
  100% {
    transform: translate(-50%, -50%) rotate(360deg) scale(1);
    opacity: 0.3;
  }
}
.starfield-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image:
    radial-gradient(2px 2px at 30px 50px, rgba(255, 255, 255, 0.8), transparent),
    radial-gradient(1px 1px at 80px 120px, rgba(96, 165, 250, 0.6), transparent),
    radial-gradient(1px 1px at 150px 40px, rgba(167, 139, 250, 0.5), transparent),
    radial-gradient(2px 2px at 200px 180px, rgba(255, 255, 255, 0.9), transparent),
    radial-gradient(1px 1px at 280px 90px, rgba(52, 211, 153, 0.4), transparent),
    radial-gradient(2px 2px at 350px 160px, rgba(236, 72, 153, 0.3), transparent);
  background-repeat: repeat;
  background-size: 400px 300px;
  animation:
    drift 20s linear infinite,
    sparkle 4s ease-in-out infinite alternate;
  pointer-events: none;
}

@keyframes drift {
  0% {
    transform: translateX(0px) translateY(0px);
  }
  100% {
    transform: translateX(-400px) translateY(-300px);
  }
}

@keyframes sparkle {
  0% {
    opacity: 0.4;
  }
  100% {
    opacity: 0.8;
  }
}

.graph-svg {
  width: 100%;
  height: 100%;
  cursor: grab;
  position: relative;
  z-index: 3;
}

.graph-svg:active {
  cursor: grabbing;
}

/* Enhanced node effects */
.node-core {
  transition: all 0.3s ease;
}

.node-glow {
  transition: all 0.3s ease;
}

.element:hover .node-core {
  filter: brightness(1.4) drop-shadow(0 0 15px currentColor);
}

.element:hover .node-glow {
  opacity: 0.8 !important;
}

.element:hover .element-label {
  fill: #ffffff;
  font-weight: bold;
  filter: drop-shadow(0 0 6px rgba(255, 255, 255, 0.8));
}

/* Animated links */
.link {
  transition: all 0.3s ease;
  stroke-dasharray: 4, 6;
  animation: energy-flow 3s linear infinite;
}

@keyframes energy-flow {
  0% {
    stroke-dashoffset: 0;
    stroke-opacity: 0.4;
  }
  50% {
    stroke-opacity: 0.7;
  }
  100% {
    stroke-dashoffset: 10;
    stroke-opacity: 0.4;
  }
}

.link:hover {
  stroke: #60a5fa;
  stroke-width: 3;
  filter: drop-shadow(0 0 8px #60a5fa);
  stroke-opacity: 0.9 !important;
}

/* Particle effects */
.particles circle {
  animation: orbit 4s linear infinite;
}

@keyframes orbit {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* Nebula background effect */
.nebula-background {
  animation: nebula-pulse 6s ease-in-out infinite alternate;
}

@keyframes nebula-pulse {
  0% {
    opacity: 0.2;
    transform: scale(0.95);
  }
  100% {
    opacity: 0.4;
    transform: scale(1.05);
  }
}

/* Node sparkle effect */
.node-sparkle {
  animation: sparkle-twinkle 2s ease-in-out infinite alternate;
}

@keyframes sparkle-twinkle {
  0% {
    opacity: 0.6;
    transform: scale(0.8);
  }
  100% {
    opacity: 1;
    transform: scale(1.2);
  }
}

/* Minimap */
.minimap-container {
  position: absolute;
  bottom: 20px;
  right: 20px;
  background: rgba(0, 0, 0, 0.85);
  padding: 12px;
  border-radius: 12px;
  border: 2px solid rgba(59, 130, 246, 0.3);
  backdrop-filter: blur(15px);
  box-shadow: 0 0 25px rgba(0, 0, 0, 0.5);
}

.minimap-svg {
  cursor: pointer;
  border: 1px solid rgba(75, 85, 99, 0.5);
  border-radius: 6px;
  background: rgba(15, 15, 35, 0.8);
}

/* Info panel */
.info-panel {
  position: absolute;
  top: 20px;
  left: 20px;
  background: rgba(0, 0, 0, 0.9);
  padding: 16px;
  border-radius: 12px;
  border: 2px solid rgba(59, 130, 246, 0.3);
  font-size: 0.9rem;
  max-width: 320px;
  backdrop-filter: blur(15px);
  box-shadow: 0 0 30px rgba(0, 0, 0, 0.5);
}

.info-panel > div {
  margin: 4px 0;
}

.info-panel strong {
  color: #60a5fa;
  font-size: 1.1rem;
}

.legend {
  margin-top: 12px;
  font-size: 0.8rem;
  opacity: 0.9;
  border-top: 1px solid rgba(75, 85, 99, 0.3);
  padding-top: 8px;
}

.legend > div {
  margin: 4px 0;
  display: flex;
  align-items: center;
}

.legend-icon {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 6px;
}

.legend-icon.series-cluster {
  background: #3b82f6;
}

.legend-icon.mega-cluster {
  background: #10b981;
}

.legend-icon.anime-node {
  background: #3b82f6;
}

.legend-icon.manga-node {
  background: #ec4899;
}

.legend-icon.other-node {
  background: #6b7280;
}

.instructions {
  font-size: 0.75rem;
  opacity: 0.8;
  margin-top: 8px;
  border-top: 1px solid rgba(75, 85, 99, 0.3);
  padding-top: 6px;
}

.instructions > div {
  margin: 2px 0;
}

/* Controls */
.controls-panel {
  position: absolute;
  top: 20px;
  right: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.control-button {
  background: rgba(0, 0, 0, 0.85);
  color: white;
  border: 2px solid rgba(59, 130, 246, 0.3);
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(15px);
  min-width: 100px;
}

.control-button:hover {
  background: rgba(59, 130, 246, 0.2);
  border-color: #60a5fa;
  box-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
  transform: translateY(-2px);
}

.back-button {
  background: rgba(59, 130, 246, 0.2);
  border-color: #3b82f6;
  color: #60a5fa;
}

.back-button:hover {
  background: rgba(59, 130, 246, 0.4);
  color: white;
  box-shadow: 0 0 25px rgba(59, 130, 246, 0.5);
}

/* Breadcrumb */
.breadcrumb {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.9);
  padding: 12px 20px;
  border-radius: 12px;
  border: 2px solid rgba(59, 130, 246, 0.3);
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 12px;
  backdrop-filter: blur(15px);
  max-width: 600px;
  overflow-x: auto;
  box-shadow: 0 0 30px rgba(0, 0, 0, 0.5);
}

.breadcrumb-item {
  cursor: pointer;
  color: #60a5fa;
  white-space: nowrap;
  transition: all 0.2s ease;
  padding: 4px 8px;
  border-radius: 6px;
}

.breadcrumb-item:hover {
  color: #3b82f6;
  background: rgba(59, 130, 246, 0.1);
  transform: scale(1.05);
}

.breadcrumb-separator {
  color: rgba(156, 163, 175, 0.6);
  margin: 0 4px;
  font-weight: bold;
}

/* Tooltip */
.tooltip {
  position: absolute;
  background: rgba(0, 0, 0, 0.95);
  padding: 16px;
  border-radius: 12px;
  border: 2px solid rgba(59, 130, 246, 0.4);
  font-size: 0.9rem;
  max-width: 320px;
  z-index: 50;
  pointer-events: none;
  backdrop-filter: blur(20px);
  box-shadow:
    0 10px 25px rgba(0, 0, 0, 0.5),
    0 0 30px rgba(59, 130, 246, 0.2);
}

.tooltip-title {
  font-weight: bold;
  margin-bottom: 8px;
  color: #f9fafb;
  border-bottom: 1px solid rgba(75, 85, 99, 0.4);
  padding-bottom: 6px;
  font-size: 1rem;
}

.tooltip-item {
  color: #d1d5db;
  margin: 4px 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Enhanced element labels */
.element-label {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.9);
  transition: all 0.3s ease;
}

/* Error container */
.error-container {
  text-align: center;
  padding: 40px;
  background: rgba(239, 68, 68, 0.1);
  border: 2px solid rgba(239, 68, 68, 0.3);
  border-radius: 12px;
  color: #fca5a5;
  position: relative;
  z-index: 2;
}

/* Responsive design */
@media (max-width: 1200px) {
  .info-panel {
    max-width: 280px;
    font-size: 0.85rem;
  }

  .controls-panel {
    gap: 8px;
  }

  .control-button {
    padding: 10px 12px;
    font-size: 0.85rem;
    min-width: 80px;
  }
}

@media (max-width: 768px) {
  .clustered-graph-container {
    padding: 16px;
    padding-top: 40px;
  }

  .canvas-container {
    height: 600px;
  }

  .info-panel {
    position: static;
    margin-bottom: 16px;
    max-width: none;
  }

  .controls-panel {
    position: static;
    flex-direction: row;
    justify-content: center;
    margin-bottom: 16px;
    flex-wrap: wrap;
  }

  .breadcrumb {
    position: static;
    transform: none;
    margin-bottom: 16px;
    justify-content: center;
    max-width: none;
  }

  .search-input-wrapper {
    max-width: none;
  }

  .graph-title {
    font-size: 1.4rem;
    text-align: center;
  }

  .minimap-container {
    bottom: 10px;
    right: 10px;
    padding: 8px;
  }
}

@media (max-width: 480px) {
  .canvas-container {
    height: 500px;
  }

  .tooltip {
    max-width: 250px;
    font-size: 0.8rem;
    padding: 12px;
  }

  .search-input {
    padding: 10px 16px;
    font-size: 13px;
  }

  .control-button {
    padding: 8px 10px;
    font-size: 0.8rem;
    min-width: 70px;
  }
}

/* Focus and accessibility */
.control-button:focus,
.search-input:focus,
.breadcrumb-item:focus {
  outline: 2px solid #60a5fa;
  outline-offset: 2px;
}

/* Loading pulse animation */
@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.loading-container {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* Smooth transitions for all interactive elements */
* {
  transition:
    opacity 0.2s ease,
    transform 0.2s ease;
}

/* Custom scrollbar for search results */
.search-results::-webkit-scrollbar {
  width: 6px;
}

.search-results::-webkit-scrollbar-track {
  background: rgba(75, 85, 99, 0.2);
  border-radius: 3px;
}

.search-results::-webkit-scrollbar-thumb {
  background: rgba(59, 130, 246, 0.5);
  border-radius: 3px;
}

.search-results::-webkit-scrollbar-thumb:hover {
  background: rgba(59, 130, 246, 0.7);
}
@keyframes connection-pulse {
  0%,
  100% {
    stroke-opacity: 0;
    stroke-width: 1;
  }
  50% {
    stroke-opacity: 0.6;
    stroke-width: 4;
  }
}
/* Enhanced node styles */
.node-hexagon {
  transition: all 0.3s ease;
}

.node-anime {
  transition: all 0.3s ease;
}

.node-manga {
  transition: all 0.3s ease;
}

.node-other {
  transition: all 0.3s ease;
}

/* Cluster composition styles */
.cluster-composition {
  pointer-events: none;
}

.cluster-composition path {
  transition: opacity 0.3s ease;
}

.element:hover .cluster-composition path {
  opacity: 1 !important;
}

/* Enhanced link styles */
.link-group {
  transition: opacity 0.3s ease;
}

.link-base {
  transition: all 0.3s ease;
}

.link-energy {
  transition: all 0.3s ease;
}

.link-pulse {
  transition: all 0.3s ease;
}

/* Hover ring animation */
.hover-ring {
  pointer-events: none;
}

/* Enhanced energy flow animation */
@keyframes energy-flow {
  0% {
    stroke-dashoffset: 0;
    stroke-opacity: 0.4;
  }
  25% {
    stroke-opacity: 0.8;
  }
  50% {
    stroke-dashoffset: 8;
    stroke-opacity: 0.6;
  }
  75% {
    stroke-opacity: 0.9;
  }
  100% {
    stroke-dashoffset: 16;
    stroke-opacity: 0.4;
  }
}

/* Node type specific hover effects */
.element:hover .node-hexagon {
  filter: drop-shadow(0 0 12px currentColor) brightness(1.3);
}

.element:hover .node-anime {
  filter: drop-shadow(0 0 8px #3b82f6) brightness(1.3);
  transform: scale(1.2) rotate(5deg);
}

.element:hover .node-manga {
  filter: drop-shadow(0 0 8px #ec4899) brightness(1.3);
  transform: scale(1.2) rotate(-5deg);
}

.element:hover .node-other {
  filter: drop-shadow(0 0 8px #10b981) brightness(1.3);
}
</style>
