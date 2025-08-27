<template>
  <div class="clustered-graph-container">
    <h1 class="graph-title">Hierarchical Anime/Manga Relations Graph</h1>

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
          <div>🟦 Series Clusters &nbsp; 🟢 Mega Clusters</div>
          <div>🔵 Anime &nbsp; 🟣 Manga &nbsp; ⚫ Standalone</div>
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

/**
 * =========================
 * Reactive state - Fixed to prevent recursive updates
 * =========================
 */
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

/**
 * =========================
 * Computed properties to prevent reactive mutations
 * =========================
 */
const svgDimensions = computed(() => ({
  width: 2400,
  height: 1600,
}))

const visibleElementsCount = computed(() => visibleElements.value.length)

/**
 * =========================
 * Refs / graph state - Fixed references
 * =========================
 */
const svgRef = ref(null)
const minimapRef = ref(null)

// Non-reactive D3 variables to prevent recursive updates
let svg, container, zoom, simulation
let nodeMap = new Map()
let latestSeriesClusters = []

/**
 * =========================
 * Constants
 * =========================
 */
const VIEW_LEVELS = {
  OVERVIEW: 'Overview',
  MEGA_CLUSTER: 'Mega Cluster',
  SERIES_CLUSTER: 'Series Cluster',
}

const STANDALONE_GROUP_SIZE = 300
const MEGA_CLUSTER_THRESHOLD = 150
const MEGA_CLUSTER_SIZE = 12
const MAX_ITEMS_VISIBLE_IN_CLUSTER = 1500

/**
 * =========================
 * Web Worker (inline)
 * =========================
 */
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
        // Sort standalone items by type for better grouping
        standaloneItems.sort((a, b) => {
          const typeA = a.type || 'unknown'
          const typeB = b.type || 'unknown'
          return typeA.localeCompare(typeB)
        })
        
        for (let i = 0; i < standaloneItems.length; i += standaloneGroupSize) {
          const group = standaloneItems.slice(i, i + standaloneGroupSize)
          const groupType = group[0]?.type || 'mixed'
          const groupName = group.length === 1 
            ? (group[0].label || group[0].name || 'Standalone Item')
            : group.length <= 20 
              ? 'Standalone ' + groupType.charAt(0).toUpperCase() + groupType.slice(1)
              : 'Standalone Group ' + Math.floor(i / standaloneGroupSize + 1)
          
          seriesClusters.push({
            id: 'standalone_group_' + Math.floor(i / standaloneGroupSize),
            name: groupName,
            itemIds: group.map(x => x.id),
            size: group.length,
            clusterType: 'standalone',
            isCluster: true,
            connectionDensity: 0
          })
        }
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

/**
 * =========================
 * Rendering helpers
 * =========================
 */
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

/**
 * =========================
 * D3 rendering
 * =========================
 */
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

  zoom = d3
    .zoom()
    .scaleExtent([0.1, 10])
    .on('zoom', (event) => {
      const { transform } = event
      container.attr('transform', transform)
      zoomLevel.value = transform.k
    })
  svg.call(zoom)

  // Add a background rect for debugging
  container
    .append('rect')
    .attr('width', svgDimensions.value.width)
    .attr('height', svgDimensions.value.height)
    .attr('fill', 'none')
    .attr('stroke', '#444')
    .attr('stroke-width', 2)
    .attr('stroke-dasharray', '5,5')

  return true
}

function renderMinimap() {
  if (!minimapRef.value || visibleElements.value.length === 0) return
  const minimap = d3.select(minimapRef.value)
  minimap.selectAll('*').remove()

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
    .attr('r', (d) => (d.isCluster ? 4 : 2))
    .attr('fill', (d) => getElementColor(d))
    .attr('opacity', 0.8)
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
    x: d.x || svgDimensions.value.width / 2 + (Math.random() - 0.5) * 50, // Reduced initial spread
    y: d.y || svgDimensions.value.height / 2 + (Math.random() - 0.5) * 50, // Reduced initial spread
  }))

  // Create node lookup map for link references
  const nodeById = new Map(elemsCopy.map((node) => [node.id, node]))

  // Process links to ensure they reference actual nodes
  const processedLinks = links
    .map((link) => {
      const sourceId = typeof link.source === 'object' ? link.source.id : link.source
      const targetId = typeof link.target === 'object' ? link.target.id : link.target
      const source = nodeById.get(sourceId)
      const target = nodeById.get(targetId)
      return source && target ? { source, target } : null
    })
    .filter(Boolean)

  // Create simulation with adjusted forces
  simulation = d3
    .forceSimulation(elemsCopy)
    .force('charge', d3.forceManyBody().strength(-200)) // Reduced repulsion
    .force(
      'center',
      d3.forceCenter(svgDimensions.value.width / 2, svgDimensions.value.height / 2).strength(0.1),
    )
    .force(
      'collision',
      d3
        .forceCollide()
        .radius((d) => (elementType === 'cluster' ? Math.max(30, Math.sqrt(d.size || 1) * 5) : 20))
        .strength(0.5),
    )

  // Add link force if we have links
  if (processedLinks.length > 0) {
    simulation.force(
      'link',
      d3
        .forceLink(processedLinks)
        .id((d) => d.id)
        .distance(50) // Reduced link distance
        .strength(1), // Increased link strength
    )

    // Create links
    container
      .append('g')
      .attr('class', 'links')
      .selectAll('line')
      .data(processedLinks)
      .join('line')
      .attr('class', 'link')
      .attr('stroke', '#6B7280')
      .attr('stroke-width', 1)
      .attr('stroke-opacity', 0.3)
  }

  // Create nodes
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

  // Add circles to nodes
  elementGroups
    .append('circle')
    .attr('r', (d) => {
      if (elementType === 'cluster') {
        const baseRadius = 20
        const sizeRadius = Math.sqrt(d.size || 1) * 3
        const maxRadius = 60 // Reduced maximum radius
        return Math.min(maxRadius, Math.max(baseRadius, sizeRadius))
      } else {
        return 12 // Slightly smaller nodes
      }
    })
    .attr('fill', (d) => getElementColor(d))
    .attr('stroke', (d) => getElementStrokeColor(d))
    .attr('stroke-width', 2)

  // Add labels
  elementGroups
    .append('text')
    .attr('class', 'element-label')
    .attr('text-anchor', 'middle')
    .attr('dy', (d) => {
      if (elementType === 'cluster') {
        const baseRadius = 20
        const sizeRadius = Math.sqrt(d.size || 1) * 3
        const maxRadius = 60
        const radius = Math.min(maxRadius, Math.max(baseRadius, sizeRadius))
        return radius + 16
      } else {
        return 12 + 16
      }
    })
    .attr('fill', '#E5E7EB')
    .attr('font-size', (d) => {
      if (elementType === 'cluster') {
        const baseSize = Math.max(10, Math.min(14, Math.log(d.size || 1) * 2 + 8))
        return baseSize + 'px'
      } else {
        return '10px'
      }
    })
    .attr('font-weight', elementType === 'cluster' ? 'bold' : 'normal')
    .style('pointer-events', 'none')
    .text((d) => {
      const name = d.name || d.label || `${d.type} ${d.id}`
      const maxLength = elementType === 'cluster' ? (d.size > 100 ? 30 : d.size > 50 ? 25 : 20) : 22
      return name.length > maxLength ? name.substring(0, maxLength - 3) + '...' : name
    })

  // Update positions on each tick
  simulation.on('tick', () => {
    // Update link positions
    container
      .selectAll('.link')
      .attr('x1', (d) => d.source.x)
      .attr('y1', (d) => d.source.y)
      .attr('x2', (d) => d.target.x)
      .attr('y2', (d) => d.target.y)

    // Update node positions
    elementGroups.attr('transform', (d) => `translate(${d.x},${d.y})`)
  })

  // Heat up the simulation
  simulation.alpha(1).restart()

  // Update visible elements
  nextTick(() => {
    visibleElements.value = elemsCopy
    setTimeout(() => renderMinimap(), 100)
  })
}

/**
 * =========================
 * View transitions
 * =========================
 */
function renderOverview() {
  currentCluster.value = null
  currentViewLevel.value = VIEW_LEVELS.OVERVIEW
  renderClusters(Array.from(clusters.value.values()))
}

function renderClusters(clusterArray) {
  console.log(`Rendering ${clusterArray.length} clusters`)

  // Sort clusters by size for better positioning
  const sortedClusters = [...clusterArray].sort((a, b) => b.size - a.size)

  sortedClusters.forEach((c, i) => {
    // Better initial positioning based on cluster size and index
    const totalClusters = sortedClusters.length
    const ring = Math.floor(Math.sqrt(i)) // Which ring to place in
    const ringRadius =
      Math.min(svgDimensions.value.width, svgDimensions.value.height) * (0.2 + ring * 0.15)
    const ringSize = Math.max(1, Math.ceil(Math.sqrt(totalClusters)) - ring) // Items in this ring
    const angleStep = (2 * Math.PI) / Math.max(ringSize, 1)
    const angle = (i % ringSize) * angleStep

    // Add some randomness but keep structure
    const jitterX = (Math.random() - 0.5) * 50
    const jitterY = (Math.random() - 0.5) * 50

    c.x = svgDimensions.value.width / 2 + Math.cos(angle) * ringRadius + jitterX
    c.y = svgDimensions.value.height / 2 + Math.sin(angle) * ringRadius + jitterY
    c.isCluster = true
  })

  renderElements(sortedClusters, 'cluster')
}

function renderClusterDetail(cluster) {
  console.log('Rendering cluster:', cluster)
  let items = []

  // Handle mega clusters differently
  if (cluster.clusterType === 'mega' && cluster.clusters) {
    // Collect all items from all sub-clusters
    items = cluster.clusters.flatMap((subCluster) => {
      if (subCluster.itemIds) {
        return subCluster.itemIds.map((id) => nodeMap.get(id)).filter(Boolean)
      }
      return []
    })
  } else {
    // Handle regular series clusters
    if (cluster.items && cluster.items.length > 0) {
      items = cluster.items.filter((item) => item && item.id)
    } else if (cluster.itemIds && cluster.itemIds.length > 0) {
      items = cluster.itemIds.map((id) => nodeMap.get(id)).filter(Boolean)
    }
  }

  console.log(`Found ${items.length} items in cluster`)

  // Create map for quick lookup
  const validItemsMap = new Map(items.map((item) => [item.id, item]))

  // Process links
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
/**
 * =========================
 * Events / interactions
 * =========================
 */
function handleElementMouseover(event, d) {
  hoveredElement.value = d
  tooltipPos.value = { x: event.pageX + 10, y: event.pageY - 10 }
}

function handleElementMouseout() {
  hoveredElement.value = null
}

function handleElementClick(event, d) {
  // Selection hooks here if needed
  console.log('Element clicked:', d)
}

function handleElementDoubleClick(event, d) {
  if (d.isCluster) {
    // For mega clusters, add both the mega cluster and its sub-clusters to the breadcrumb
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

/**
 * =========================
 * Navigation
 * =========================
 */
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

/**
 * =========================
 * Search
 * =========================
 */
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

  // Find series cluster containing this node
  const targetCluster = latestSeriesClusters.find((c) => (c.itemIds || []).includes(node.id))
  if (targetCluster) {
    breadcrumb.value = []
    renderClusterDetail(targetCluster)
    // Center on node after layout warms up
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
    }, 600)
  }
}

/**
 * =========================
 * Zoom controls
 * =========================
 */
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

/**
 * =========================
 * Initialization
 * =========================
 */
async function initializeVisualization(clusterPayload) {
  console.log('🚀 Initializing hierarchical visualization...')
  console.log('Clusters received:', clusterPayload.clusters.length)

  // Wait for DOM to be fully ready
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

  // Write clusters Map
  const clusterMap = new Map()
  clusterPayload.clusters.forEach((c) => {
    clusterMap.set(c.id, { ...c })
  })

  clusters.value = clusterMap
  totalClusters.value = clusterMap.size
  latestSeriesClusters = clusterPayload.seriesClusters

  // Annotate nodes with cluster info
  const idToClusterName = new Map()
  clusterPayload.seriesClusters.forEach((c) => {
    c.itemIds.forEach((id) => idToClusterName.set(id, c.name))
  })
  nodeMap.forEach((n, id) => {
    n.clusterName = idToClusterName.get(id) || 'Standalone'
  })

  // Another nextTick to ensure everything is ready
  await nextTick()
  renderOverview()
  console.log('✅ Hierarchical visualization initialized')
}

/**
 * =========================
 * Lifecycle
 * =========================
 */
onMounted(async () => {
  try {
    console.log('📡 Fetching graph data...')
    const res = await axios.get('http://127.0.0.1:8000/graph')

    const nodes = res.data.nodes || []
    const links = Array.isArray(res.data.links)
      ? res.data.links
      : Object.values(res.data.links || {})

    rawNodes.value = nodes
    rawLinks.value = links
    totalNodes.value = nodes.length

    console.log(`✅ Loaded ${nodes.length} nodes and ${links.length} links`)

    // Basic normalization + O(n+m) degree counting
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
        // Keep some color variety if type missing
        node.type = Math.random() > 0.6 ? 'anime' : Math.random() > 0.5 ? 'manga' : 'other'
      }
      node.connectionCount = degreeMap.get(node.id) || 0
      nodeMap.set(node.id, node) // Ensure all nodes are added to nodeMap
    })

    // Kick off worker clustering
    const worker = createClusterWorker()
    worker.onmessage = async (msg) => {
      const { type } = msg.data || {}
      if (type === 'progress') {
        progressText.value = msg.data.text
      } else if (type === 'done') {
        progressText.value = ''

        // Set loading to false FIRST
        loading.value = false

        // Wait for template to re-render
        await nextTick()
        await nextTick()

        // Now try to initialize
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
    console.log('nodeMap contents:', Array.from(nodeMap.keys()))
    worker.postMessage({
      nodes: cleanNodes,
      links: cleanLinks,
      standaloneGroupSize: STANDALONE_GROUP_SIZE,
      megaThreshold: MEGA_CLUSTER_THRESHOLD,
      megaSize: MEGA_CLUSTER_SIZE,
    })
  } catch (err) {
    console.error('❌ Error:', err)
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
  background-color: #111827;
  min-height: 100vh;
  color: white;
  max-width: 100%;
  margin: 0 auto;
}

.graph-title {
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 16px;
}

/* Search container */
.search-container {
  margin-bottom: 16px;
  display: flex;
  gap: 16px;
  align-items: center;
}

.search-input-wrapper {
  position: relative;
  flex: 1;
  max-width: 448px;
}

.search-input {
  width: 100%;
  padding: 8px 16px;
  background-color: #1f2937;
  border: 1px solid #4b5563;
  border-radius: 6px;
  color: white;
  outline: none;
  transition: border-color 0.2s;
}

.search-input::placeholder {
  color: #9ca3af;
}

.search-input:focus {
  border-color: #3b82f6;
}

.search-results {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background-color: #1f2937;
  border: 1px solid #4b5563;
  border-top: none;
  border-radius: 0 0 6px 6px;
  max-height: 200px;
  overflow-y: auto;
  z-index: 10;
}

.search-result-item {
  padding: 8px 16px;
  cursor: pointer;
  border-bottom: 1px solid #374151;
  transition: background-color 0.2s;
}

.search-result-item:last-child {
  border-bottom: none;
}

.search-result-item:hover {
  background-color: #374151;
}

.search-result-title {
  font-weight: 600;
  margin-bottom: 2px;
}

.search-result-subtitle {
  font-size: 0.875rem;
  color: #9ca3af;
}

/* Loading */
.loading-container {
  text-align: center;
  padding: 40px;
}

.loading-subtitle {
  font-size: 0.875rem;
  opacity: 0.7;
  margin-top: 8px;
}

/* Graph wrapper */
.graph-wrapper {
  position: relative;
}

.canvas-container {
  position: relative;
  background-color: #1f2937;
  border-radius: 8px;
  overflow: hidden;
  height: 700px;
  border: 1px solid #374151;
}

.graph-svg {
  width: 100%;
  height: 100%;
  cursor: grab;
}

.graph-svg:active {
  cursor: grabbing;
}

/* Element labels styling */
.element-label {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
}

/* Minimap */
.minimap-container {
  position: absolute;
  bottom: 16px;
  right: 16px;
  background: rgba(0, 0, 0, 0.8);
  padding: 8px;
  border-radius: 6px;
  border: 1px solid #4b5563;
}

.minimap-svg {
  cursor: pointer;
  border: 1px solid #374151;
}

/* Info panel */
.info-panel {
  position: absolute;
  top: 16px;
  left: 16px;
  background: rgba(0, 0, 0, 0.9);
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #4b5563;
  font-size: 0.875rem;
  max-width: 280px;
  backdrop-filter: blur(4px);
}

.info-panel > div {
  margin: 2px 0;
}

.legend {
  margin-top: 8px;
  font-size: 0.75rem;
  opacity: 0.9;
}

.legend > div {
  margin: 2px 0;
}

.instructions {
  font-size: 0.75rem;
  opacity: 0.8;
  margin-top: 6px;
  border-top: 1px solid #374151;
  padding-top: 4px;
}

.instructions > div {
  margin: 1px 0;
}

/* Controls */
.controls-panel {
  position: absolute;
  top: 16px;
  right: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.control-button {
  background: rgba(0, 0, 0, 0.8);
  color: white;
  border: 1px solid #4b5563;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
  backdrop-filter: blur(4px);
}

.control-button:hover {
  background-color: #374151;
  border-color: #6b7280;
}

.back-button {
  background-color: #1f2937;
  border-color: #3b82f6;
  color: #60a5fa;
}

.back-button:hover {
  background-color: #3b82f6;
  color: white;
}

/* Breadcrumb */
.breadcrumb {
  position: absolute;
  top: 16px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.9);
  padding: 8px 16px;
  border-radius: 6px;
  border: 1px solid #4b5563;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 8px;
  backdrop-filter: blur(4px);
  max-width: 500px;
  overflow-x: auto;
}

.breadcrumb-item {
  cursor: pointer;
  color: #60a5fa;
  white-space: nowrap;
  transition: color 0.2s;
}

.breadcrumb-item:hover {
  color: #3b82f6;
}

.breadcrumb-separator {
  color: #9ca3af;
  margin: 0 4px;
}

/* Tooltip */
.tooltip {
  position: absolute;
  background: rgba(0, 0, 0, 0.95);
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #4b5563;
  font-size: 0.875rem;
  max-width: 280px;
  z-index: 30;
  pointer-events: none;
  backdrop-filter: blur(4px);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.tooltip-title {
  font-weight: bold;
  margin-bottom: 6px;
  color: #f9fafb;
  border-bottom: 1px solid #374151;
  padding-bottom: 4px;
}

.tooltip-item {
  color: #d1d5db;
  margin: 3px 0;
  display: flex;
  justify-content: space-between;
}

/* Links */
.link {
  transition: opacity 0.2s;
}

/* Responsive */
@media (max-width: 768px) {
  .clustered-graph-container {
    padding: 16px;
    padding-top: 50px;
  }
  .canvas-container {
    height: 500px;
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
  }
  .breadcrumb {
    position: static;
    transform: none;
    margin-bottom: 16px;
    justify-content: center;
  }
  .search-input-wrapper {
    max-width: none;
  }
}

/* Animations & effects */
.element {
  transition: opacity 0.3s ease-in-out;
}
.element:hover circle {
  filter: brightness(1.2);
  stroke-width: 4;
}
.element:hover .element-label {
  font-weight: bold;
}

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

.info-panel strong {
  color: #60a5fa;
}
.element circle {
  transition: all 0.2s ease-in-out;
}
.element.focused circle {
  stroke: #fbbf24;
  stroke-width: 4;
  filter: drop-shadow(0 0 8px rgba(251, 191, 36, 0.5));
}
.element.focused .element-label {
  fill: #fbbf24;
  font-weight: bold;
}
</style>
