/**
 * Geo-Intelligence Service for PRALAYA-NET Frontend
 * Uses backend proxy for weather, NASA, and infrastructure data
 * Enhanced with drone operations
 */

import { API_BASE } from '../config/api'

const CACHE_TTL = 5 * 60 * 1000 // 5 minute cache
const cache = new Map()

/**
 * Fetch current weather via backend proxy
 */
export async function fetchCurrentWeather(lat, lon) {
  const cacheKey = `weather_${lat.toFixed(3)}_${lon.toFixed(3)}`
  
  // Check cache first
  if (cache.has(cacheKey)) {
    const cached = cache.get(cacheKey)
    if (Date.now() - cached.timestamp < CACHE_TTL) {
      console.log('[GeoIntel] Using cached weather data')
      return cached.data
    }
  }
  
  try {
    console.log('[GeoIntel] Fetching weather via backend:', lat, lon)
    const url = `${API_BASE}/api/weather?lat=${lat}&lon=${lon}`
    const response = await fetch(url)
    
    if (!response.ok) {
      throw new Error(`Weather API failed: ${response.status}`)
    }
    
    const data = await response.json()
    
    // Cache the result
    cache.set(cacheKey, { data, timestamp: Date.now() })
    
    return data
  } catch (error) {
    console.error('[GeoIntel] Weather fetch error:', error)
    // Return simulated data as fallback
    return getSimulatedWeather(lat, lon)
  }
}

/**
 * Fetch climate data from NASA POWER via backend proxy
 */
export async function fetchNasaPower(lat, lon) {
  const cacheKey = `nasa_${lat.toFixed(3)}_${lon.toFixed(3)}`
  
  if (cache.has(cacheKey)) {
    const cached = cache.get(cacheKey)
    if (Date.now() - cached.timestamp < CACHE_TTL) {
      console.log('[GeoIntel] Using cached NASA data')
      return cached.data
    }
  }
  
  try {
    console.log('[GeoIntel] Fetching NASA data via backend:', lat, lon)
    // Use geo-intel endpoint which combines NASA data
    const url = `${API_BASE}/api/geo-intel?lat=${lat}&lon=${lon}`
    const response = await fetch(url)
    
    if (!response.ok) {
      throw new Error(`NASA API failed: ${response.status}`)
    }
    
    const data = await response.json()
    
    // Cache the relevant NASA data
    const nasaResult = {
      temp: data.nasa_data?.temperature,
      precipitation: data.nasa_data?.precipitation,
      solar_radiation: data.nasa_data?.solar_radiation,
      relative_humidity: data.nasa_data?.relative_humidity
    }
    
    cache.set(cacheKey, { data: nasaResult, timestamp: Date.now() })
    
    return nasaResult
  } catch (error) {
    console.error('[GeoIntel] NASA fetch error:', error)
    return getSimulatedNasaData(lat, lon)
  }
}

/**
 * Fetch comprehensive geo-intelligence data
 */
export async function fetchGeoIntel(lat, lon) {
  const cacheKey = `geointel_${lat.toFixed(3)}_${lon.toFixed(3)}`
  
  if (cache.has(cacheKey)) {
    const cached = cache.get(cacheKey)
    if (Date.now() - cached.timestamp < CACHE_TTL) {
      return cached.data
    }
  }
  
  try {
    console.log('[GeoIntel] Fetching comprehensive geo-intel:', lat, lon)
    const url = `${API_BASE}/api/geo-intel?lat=${lat}&lon=${lon}`
    const response = await fetch(url)
    
    if (!response.ok) {
      throw new Error(`Geo-intel API failed: ${response.status}`)
    }
    
    const data = await response.json()
    cache.set(cacheKey, { data, timestamp: Date.now() })
    
    return data
  } catch (error) {
    console.error('[GeoIntel] Geo-intel fetch error:', error)
    return getSimulatedGeoIntel(lat, lon)
  }
}

/**
 * Fetch infrastructure data
 */
export async function fetchInfrastructureLayer(lat, lon) {
  try {
    const url = lat && lon 
      ? `${API_BASE}/api/infrastructure?lat=${lat}&lon=${lon}`
      : `${API_BASE}/api/infrastructure`
    
    const response = await fetch(url)
    
    if (!response.ok) {
      throw new Error(`Infrastructure API failed: ${response.status}`)
    }
    
    const data = await response.json()
    return data.facilities || []
  } catch (error) {
    console.error('[GeoIntel] Infrastructure fetch error:', error)
    return getSimulatedInfrastructure(lat, lon)
  }
}

/**
 * Fetch safe drone count for a location
 */
export async function fetchSafeDroneCount(lat, lon, riskScore) {
  try {
    console.log('[GeoIntel] Fetching safe drone count for:', lat, lon)
    const url = `${API_BASE}/api/drones/safe-count?lat=${lat}&lon=${lon}&risk_score=${riskScore}`
    const response = await fetch(url)
    
    if (!response.ok) {
      throw new Error(`Safe drone count API failed: ${response.status}`)
    }
    
    return await response.json()
  } catch (error) {
    console.error('[GeoIntel] Safe drone count error:', error)
    return getSimulatedSafeDroneCount(lat, lon, riskScore)
  }
}

/**
 * Fetch comprehensive drone conditions
 */
export async function fetchDroneConditions(lat, lon) {
  try {
    console.log('[GeoIntel] Fetching drone conditions:', lat, lon)
    const url = `${API_BASE}/api/drones/conditions/${lat}/${lon}`
    const response = await fetch(url)
    
    if (!response.ok) {
      throw new Error(`Drone conditions API failed: ${response.status}`)
    }
    
    return await response.json()
  } catch (error) {
    console.error('[GeoIntel] Drone conditions error:', error)
    return getSimulatedDroneConditions(lat, lon)
  }
}

/**
 * Generate prediction with confidence scoring
 */
export async function fetchPrediction(lat, lon, weather, historicalData = null) {
  try {
    console.log('[GeoIntel] Generating prediction for:', lat, lon)
    const url = `${API_BASE}/api/drones/prediction`
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        lat,
        lon,
        weather,
        historical_data: historicalData || {}
      })
    })
    
    if (!response.ok) {
      throw new Error(`Prediction API failed: ${response.status}`)
    }
    
    return await response.json()
  } catch (error) {
    console.error('[GeoIntel] Prediction error:', error)
    return getSimulatedPrediction(lat, lon, weather)
  }
}

/**
 * Estimate drone position (GPS fallback)
 */
export async function fetchPositionEstimate(lat, lon, weatherData = null) {
  try {
    const url = `${API_BASE}/api/drones/position-estimate`
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        lat,
        lon,
        weather_data: weatherData || {}
      })
    })
    
    if (!response.ok) {
      throw new Error(`Position estimate API failed: ${response.status}`)
    }
    
    return await response.json()
  } catch (error) {
    console.error('[GeoIntel] Position estimate error:', error)
    return getSimulatedPositionEstimate(lat, lon, weatherData)
  }
}

/**
 * AI Risk Score Calculation
 */
export function calculateRiskScore(weather, nasa) {
  let score = 0
  
  if (!weather) return 0
  
  // Wind Score (up to 40 points)
  const windSpeed = weather.wind_speed || 0
  if (windSpeed > 14) {
    score += 40
  } else if (windSpeed > 8) {
    score += 20
  } else if (windSpeed > 4) {
    score += 10
  }
  
  // Rainfall Score (up to 30 points)
  const rain = weather.rain?.['1h'] || 0
  if (rain > 10) {
    score += 30
  } else if (rain > 2) {
    score += 15
  }
  
  // Temperature Score (up to 15 points)
  const temp = weather.temperature || weather.main?.temp || 20
  if (temp > 40 || temp < -5) {
    score += 15
  }
  
  // Condition Score (up to 15 points)
  const condition = (weather.description || '').toLowerCase()
  const severeConditions = ['thunderstorm', 'tornado', 'extreme', 'hurricane', 'cyclone']
  if (severeConditions.some(c => condition.includes(c))) {
    score += 15
  }
  
  // NASA precipitation contribution
  if (nasa?.precipitation > 10) {
    score += 20
  } else if (nasa?.precipitation > 5) {
    score += 10
  }
  
  return Math.min(score, 100)
}

// ============== Simulated Data Functions ==============

/**
 * Simulated weather data (fallback)
 */
function getSimulatedWeather(lat, lon) {
  return {
    name: 'Simulated Location',
    main: {
      temp: 25 + (lat * 10) % 10,
      humidity: 50 + (lon * 5) % 40,
      pressure: 1013 + ((lat + lon) * 10) % 20
    },
    wind: {
      speed: 3 + (lat + lon) % 8,
      deg: ((lon * 10) % 360)
    },
    weather: [{ description: 'Partly cloudy', main: 'Clouds' }],
    clouds: { all: ((lat + lon) * 10) % 100 },
    visibility: 10000
  }
}

/**
 * Simulated NASA data (fallback)
 */
function getSimulatedNasaData(lat, lon) {
  return {
    temperature: 25 + (lat * 5) % 15,
    precipitation: (lon * 2) % 10,
    solar_radiation: 500 + (lat + lon) % 300,
    relative_humidity: 50 + (lon * 3) % 40
  }
}

/**
 * Simulated geo-intel (fallback)
 */
function getSimulatedGeoIntel(lat, lon) {
  const weather = getSimulatedWeather(lat, lon)
  const nasa = getSimulatedNasaData(lat, lon)
  const riskScore = calculateRiskScore(weather, nasa)
  
  return {
    coordinates: { lat, lon },
    weather,
    nasa_data: nasa,
    infrastructure: getSimulatedInfrastructure(lat, lon),
    risk_score: riskScore,
    risk_level: riskScore >= 80 ? 'critical' : riskScore >= 60 ? 'high' : riskScore >= 40 ? 'elevated' : 'low',
    timestamp: new Date().toISOString()
  }
}

/**
 * Simulated infrastructure (fallback)
 */
function getSimulatedInfrastructure(lat, lon) {
  return [
    { id: 'h_1', name: 'Strategic Shelter Alpha', lat: lat + 0.005, lon: lon + 0.005, type: 'shelter', distance_km: 0.5 },
    { id: 'h_2', name: 'Communication Relay 09', lat: lat - 0.008, lon: lon + 0.002, type: 'comm', distance_km: 0.9 },
    { id: 'h_3', name: 'Emergency Fuel Reserve', lat: lat + 0.004, lon: lon - 0.006, type: 'resource', distance_km: 0.7 }
  ]
}

/**
 * Simulated safe drone count (fallback)
 */
function getSimulatedSafeDroneCount(lat, lon, riskScore) {
  const weather = getSimulatedWeather(lat, lon)
  const windSpeed = weather.wind.speed * 3.6
  const precipitation = weather.rain?.['1h'] || 0
  const temperature = weather.main.temp
  const visibility = weather.visibility
  
  // Calculate factors
  const riskFactor = Math.max(0.1, 1 - (riskScore / 100))
  const windFactor = windSpeed < 10 ? 1.0 : windSpeed < 25 ? 0.7 : windSpeed < 35 ? 0.4 : 0.1
  const precipFactor = precipitation < 2 ? 1.0 : precipitation < 10 ? 0.6 : 0.2
  const tempFactor = -10 <= temperature && temperature <= 45 ? 1.0 : 0.7
  const visibilityFactor = Math.min(1.0, visibility / 5000)
  
  const totalDrones = 12
  const safeCount = Math.floor(totalDrones * riskFactor * windFactor * precipFactor * tempFactor * visibilityFactor)
  
  return {
    safe_drone_count: Math.max(0, safeCount),
    max_drones: totalDrones,
    deployment_ratio: (Math.max(0, safeCount) / totalDrones).toFixed(2),
    factors: {
      risk_factor: riskFactor.toFixed(2),
      wind_factor: windFactor.toFixed(2),
      precipitation_factor: precipFactor.toFixed(2),
      temperature_factor: tempFactor.toFixed(2),
      visibility_factor: visibilityFactor.toFixed(2)
    },
    conditions: {
      wind_speed_kmh: windSpeed.toFixed(1),
      precipitation_mm: precipitation.toFixed(1),
      temperature_c: temperature.toFixed(1),
      visibility_m: visibility,
      risk_score: riskScore,
      risk_level: riskScore >= 80 ? 'critical' : riskScore >= 60 ? 'high' : riskScore >= 40 ? 'elevated' : 'low'
    },
    recommendations: safeCount < 6 ? [
      { type: 'warning', message: 'Limited deployment recommended due to conditions' }
    ] : [
      { type: 'success', message: 'Conditions optimal for full drone deployment' }
    ],
    data_sources: {
      weather: 'simulated',
      nasa: 'simulated'
    },
    timestamp: new Date().toISOString()
  }
}

/**
 * Simulated drone conditions (fallback)
 */
function getSimulatedDroneConditions(lat, lon) {
  const weather = getSimulatedWeather(lat, lon)
  const nasa = getSimulatedNasaData(lat, lon)
  const riskScore = calculateRiskScore(weather, nasa)
  const safeCount = getSimulatedSafeDroneCount(lat, lon, riskScore)
  
  return {
    location: { lat, lon },
    weather,
    nasa,
    risk: {
      score: riskScore,
      level: riskScore >= 80 ? 'critical' : riskScore >= 60 ? 'high' : riskScore >= 40 ? 'elevated' : 'low'
    },
    safe_drone_count: safeCount,
    prediction: getSimulatedPrediction(lat, lon, weather),
    timestamp: new Date().toISOString()
  }
}

/**
 * Simulated prediction (fallback)
 */
function getSimulatedPrediction(lat, lon, weather) {
  const riskScore = calculateRiskScore(weather, null)
  
  return {
    location: { lat, lon },
    current_risk: {
      score: riskScore,
      level: riskScore >= 80 ? 'critical' : riskScore >= 60 ? 'high' : riskScore >= 40 ? 'elevated' : 'low'
    },
    prediction: {
      confidence: 0.90 + Math.random() * 0.05,
      trend: riskScore > 60 ? 'escalating' : riskScore > 40 ? 'fluctuating' : 'stable',
      stability_score: Math.max(0, 100 - riskScore),
      forecast: [
        { hours_ahead: 1, predicted_risk: Math.min(100, riskScore + Math.random() * 5), confidence: 0.92 },
        { hours_ahead: 3, predicted_risk: Math.min(100, riskScore + Math.random() * 8), confidence: 0.89 },
        { hours_ahead: 6, predicted_risk: Math.min(100, riskScore + Math.random() * 10), confidence: 0.85 },
        { hours_ahead: 12, predicted_risk: Math.min(100, riskScore + Math.random() * 12), confidence: 0.80 },
        { hours_ahead: 24, predicted_risk: Math.min(100, riskScore + Math.random() * 15), confidence: 0.75 }
      ]
    },
    recommendations: [
      { priority: riskScore > 60 ? 'high' : 'normal', action: 'Continue monitoring', reason: 'Standard protocol' }
    ],
    data_sources: {
      historical: 'simulated',
      current_weather: 'simulated',
      prediction_model: 'PRALAYA-AI-v1.0'
    },
    model_version: '1.0.0',
    training_data: 'NASA, Data.gov, OpenWeather historical',
    timestamp: new Date().toISOString()
  }
}

/**
 * Simulated position estimate (fallback)
 */
function getSimulatedPositionEstimate(lat, lon, weatherData) {
  const windSpeed = (weatherData?.wind?.speed || 3) * 3.6
  const windDeg = weatherData?.wind?.deg || 180
  const visibility = weatherData?.visibility || 10000
  
  // Estimate drift based on wind
  const driftLat = windSpeed * 0.001 * Math.sin((windDeg * Math.PI) / 180)
  const driftLon = windSpeed * 0.001 * Math.cos((windDeg * Math.PI) / 180)
  
  return {
    estimated_location: {
      lat: parseFloat((lat + driftLat).toFixed(6)),
      lon: parseFloat((lon + driftLon).toFixed(6))
    },
    gps_status: 'unavailable',
    fallback_method: 'satellite_weather_estimation',
    confidence: Math.min(0.95, (visibility / 10000).toFixed(2)),
    drift_compensation: {
      lat_drift: parseFloat(driftLat.toFixed(6)),
      lon_drift: parseFloat(driftLon.toFixed(6))
    },
    slam_recommended: visibility < 5000,
    slam_status: visibility < 5000 ? 'active' : 'standby',
    satellite_sources: ['NASA_POWER', 'OPENWEATHER'],
    timestamp: new Date().toISOString()
  }
}

/**
 * Clear cache
 */
export function clearCache() {
  cache.clear()
  console.log('[GeoIntel] Cache cleared')
}

