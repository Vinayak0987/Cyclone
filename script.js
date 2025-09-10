// AstroAlert Frontend JavaScript

// DOM Elements
const analysisForm = document.getElementById('analysisForm');
const imageUpload = document.getElementById('imageUpload');
const datetimeInput = document.getElementById('datetime');
const enhancedToggle = document.getElementById('enhancedToggle');
const enhancedFeatures = document.getElementById('enhancedFeatures');
const loadingSection = document.getElementById('loadingSection');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');
const previewImage = document.getElementById('previewImage');
const uploadText = document.querySelector('.upload-text');
const loadingSteps = document.getElementById('loadingSteps');
const enhancedLoadingSteps = document.getElementById('enhancedLoadingSteps');
const enhancedResultsCard = document.getElementById('enhancedResultsCard');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    checkServerConnection();
    
    // Set up periodic connection check (every 10 seconds)
    setInterval(() => {
        checkServerConnection();
    }, 10000);
});

function initializeApp() {
    // Set current datetime as default
    const now = new Date();
    const localDateTime = new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
    datetimeInput.value = localDateTime;

    // Add event listeners
    analysisForm.addEventListener('submit', handleFormSubmission);
    imageUpload.addEventListener('change', handleImageUpload);
    enhancedToggle.addEventListener('change', handleEnhancedToggle);

    // Add loading step animation
    setupLoadingAnimation();
}

async function checkServerConnection() {
    try {
        // Try multiple URLs to ensure we connect to the right server
        const urls = [
            '/api/health',
            'http://localhost:5000/api/health',
            'http://127.0.0.1:5000/api/health'
        ];
        
        let response = null;
        let data = null;
        
        for (const url of urls) {
            try {
                console.log(`🔍 Trying to connect to: ${url}`);
                response = await fetch(url);
                if (response.ok) {
                    data = await response.json();
                    console.log(`✅ Successfully connected to: ${url}`);
                    break;
                }
            } catch (urlError) {
                console.log(`❌ Failed to connect to: ${url}`);
                continue;
            }
        }
        
        if (data && data.status === 'healthy' && data.astroalert_ready) {
            console.log('✅ Server connection successful - Real backend ready!');
            showConnectionStatus(true);
        } else if (response && response.ok) {
            console.log('⚠️ Server connected but AstroAlert not ready');
            showConnectionStatus(false);
        } else {
            throw new Error('No working server found');
        }
    } catch (error) {
        console.log('🔄 Server not available - Using demo mode', error);
        showConnectionStatus(false, true);
    }
}

function showConnectionStatus(connected, demoMode = false) {
    // Remove any existing status elements
    const existingStatus = document.querySelectorAll('.connection-status');
    existingStatus.forEach(el => el.remove());
    
    const statusElement = document.createElement('div');
    statusElement.className = 'connection-status';
    statusElement.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 10px 15px;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: 500;
        z-index: 1000;
        transition: all 0.3s ease;
        cursor: pointer;
    `;
    
    if (connected) {
        statusElement.textContent = '✅ Real Backend Connected';
        statusElement.style.background = 'rgba(46, 204, 113, 0.9)';
        statusElement.style.color = 'white';
    } else if (demoMode) {
        statusElement.textContent = '🎭 Demo Mode - Click to retry connection';
        statusElement.style.background = 'rgba(243, 156, 18, 0.9)';
        statusElement.style.color = 'white';
        
        // Add click handler to retry connection
        statusElement.addEventListener('click', () => {
            console.log('🔄 Retrying server connection...');
            statusElement.textContent = '🔄 Connecting...';
            checkServerConnection();
        });
    } else {
        statusElement.textContent = '⚠️ Backend Issue - Click to retry';
        statusElement.style.background = 'rgba(231, 76, 60, 0.9)';
        statusElement.style.color = 'white';
        
        // Add click handler to retry connection
        statusElement.addEventListener('click', () => {
            console.log('🔄 Retrying server connection...');
            statusElement.textContent = '🔄 Connecting...';
            checkServerConnection();
        });
    }
    
    document.body.appendChild(statusElement);
    
    // Auto-remove after 8 seconds for success, keep longer for errors
    const removeDelay = connected ? 5000 : 15000;
    setTimeout(() => {
        if (statusElement.parentNode) {
            statusElement.remove();
        }
    }, removeDelay);
}

function handleEnhancedToggle(event) {
    const isEnhanced = event.target.checked;
    
    if (isEnhanced) {
        enhancedFeatures.style.display = 'block';
        enhancedFeatures.style.maxHeight = '200px';
        enhancedFeatures.style.opacity = '1';
        document.getElementById('combinedAssessmentTitle').textContent = 'Enhanced Combined Assessment';
    } else {
        enhancedFeatures.style.display = 'none';
        enhancedFeatures.style.maxHeight = '0';
        enhancedFeatures.style.opacity = '0';
        document.getElementById('combinedAssessmentTitle').textContent = 'Combined Assessment';
    }
}

function handleImageUpload(event) {
    const file = event.target.files[0];
    if (file) {
        uploadText.textContent = file.name;
        
        // Create preview
        const reader = new FileReader();
        reader.onload = function(e) {
            previewImage.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }
}

async function handleFormSubmission(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const latitude = parseFloat(formData.get('latitude'));
    const longitude = parseFloat(formData.get('longitude'));
    const datetime = formData.get('datetime');
    const image = formData.get('image');
    const enhanced = enhancedToggle.checked;

    // Validate inputs
    if (!image) {
        showError('Please select a satellite image to analyze.');
        return;
    }

    if (!latitude || !longitude) {
        showError('Please enter valid latitude and longitude coordinates.');
        return;
    }

    if (!datetime) {
        showError('Please select date and time for analysis.');
        return;
    }

    // Start analysis
    await performAnalysis({
        image: image,
        latitude: latitude,
        longitude: longitude,
        datetime: datetime,
        enhanced: enhanced
    });
}

async function performAnalysis(data) {
    try {
        hideAllSections();
        showLoadingSection(data.enhanced);
        
        // Simulate analysis steps (keep for visual effect)
        const analysisStepsPromise = simulateAnalysisSteps(data.enhanced);
        
        // Make real API call to Flask backend
        const formData = new FormData();
        formData.append('image', data.image);
        formData.append('latitude', data.latitude);
        formData.append('longitude', data.longitude);
        formData.append('datetime', data.datetime);
        formData.append('enhanced', data.enhanced ? 'true' : 'false');
        
        console.log('📡 Sending request to backend API...');
        
        // Try multiple URLs to ensure we connect to the right server
        const apiUrls = [
            '/api/analyze',
            'http://localhost:5000/api/analyze',
            'http://127.0.0.1:5000/api/analyze'
        ];
        
        let response = null;
        for (const apiUrl of apiUrls) {
            try {
                console.log(`🔍 Trying API call to: ${apiUrl}`);
                response = await fetch(apiUrl, {
                    method: 'POST',
                    body: formData
                });
                if (response.ok) {
                    console.log(`✅ API call successful to: ${apiUrl}`);
                    break;
                }
            } catch (urlError) {
                console.log(`❌ API call failed to: ${apiUrl}`);
                continue;
            }
        }
        
        if (!response || !response.ok) {
            throw new Error('All API endpoints failed');
        }
        
        const results = await response.json();
        
        // Wait for loading animation to complete
        await analysisStepsPromise;
        
        if (results.success) {
            console.log('✅ Analysis completed successfully:', results);
            hideLoadingSection();
            if (data.enhanced && results.results && results.results.combined_enhanced) {
                displayEnhancedResults(results);
            } else {
                displayRealResults(results);
            }
        } else {
            console.error('❌ Analysis failed:', results.error);
            hideLoadingSection();
            showError(results.error || 'Analysis failed. Please try again.');
        }
        
    } catch (error) {
        console.error('❌ Network or parsing error:', error);
        console.log('🔄 Falling back to demo mode...');
        
        // Fallback to mock analysis
        try {
            const mockResults = await generateMockResults(data);
            hideLoadingSection();
            displayResults(mockResults);
            
            // Show demo mode indicator
            showConnectionStatus(false, true);
        } catch (mockError) {
            hideLoadingSection();
            showError('Analysis failed. Please check your internet connection and try again.');
        }
    }
}

async function simulateAnalysisSteps(isEnhanced = false) {
    const stepsContainer = isEnhanced ? enhancedLoadingSteps : loadingSteps;
    const steps = stepsContainer.querySelectorAll('.step');
    
    for (let i = 0; i < steps.length; i++) {
        // Remove active class from all steps
        steps.forEach(step => step.classList.remove('active'));
        
        // Add active class to current step
        steps[i].classList.add('active');
        
        // Wait for step to complete
        await new Promise(resolve => setTimeout(resolve, 1500));
    }
}

async function generateMockResults(inputData) {
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Generate mock results based on location and random factors
    const mockDetection = generateMockDetectionResults(inputData.latitude, inputData.longitude);
    const mockAstrology = generateMockAstrologyResults(inputData.datetime, inputData.latitude, inputData.longitude);
    const mockCombined = generateMockCombinedResults(mockDetection, mockAstrology);
    
    return {
        detection: mockDetection,
        astrology: mockAstrology,
        combined: mockCombined,
        timestamp: new Date().toISOString(),
        inputData: inputData
    };
}

function generateMockDetectionResults(latitude, longitude) {
    // Simulate cyclone detection based on location proximity to known cyclone-prone areas
    const cycloneCount = Math.random() > 0.7 ? Math.floor(Math.random() * 3) + 1 : 0;
    const avgConfidence = cycloneCount > 0 ? 0.3 + Math.random() * 0.6 : 0;
    
    let aiRiskScore = 0;
    if (cycloneCount > 0) {
        if (avgConfidence > 0.8) aiRiskScore = 30;
        else if (avgConfidence > 0.5) aiRiskScore = 20;
        else if (avgConfidence > 0.2) aiRiskScore = 10;
    }
    
    return {
        total_cyclones: cycloneCount,
        avg_confidence: avgConfidence,
        max_confidence: cycloneCount > 0 ? Math.max(avgConfidence + 0.1, 1) : 0,
        ai_risk_score: aiRiskScore,
        detections: Array.from({ length: cycloneCount }, (_, i) => ({
            bbox: [100 + i * 50, 100 + i * 40, 200 + i * 50, 200 + i * 40],
            confidence: avgConfidence + (Math.random() - 0.5) * 0.2,
            class: 0
        }))
    };
}

function generateMockAstrologyResults(datetime, latitude, longitude) {
    const date = new Date(datetime);
    const month = date.getMonth() + 1;
    const day = date.getDate();
    
    // Simulate VRS score based on date and location
    let vrsScore = 20 + Math.random() * 60; // Base score 20-80
    
    // Adjust for monsoon season (June-September in India)
    if (month >= 6 && month <= 9) {
        vrsScore += 10;
    }
    
    // Adjust for coastal regions (higher risk)
    if (Math.abs(latitude - 19.0760) < 5 && Math.abs(longitude - 72.8777) < 5) {
        vrsScore += 5;
    }
    
    vrsScore = Math.min(95, Math.max(5, vrsScore));
    
    let riskLevel, riskFactors;
    if (vrsScore >= 70) {
        riskLevel = 'EXTREME';
        riskFactors = ['Mars in 8th house', 'Rahu-Ketu axis unfavorable', 'Malefic planetary combinations'];
    } else if (vrsScore >= 50) {
        riskLevel = 'HIGH';
        riskFactors = ['Saturn transit effects', 'New moon phase influence', 'Seasonal planetary positions'];
    } else if (vrsScore >= 30) {
        riskLevel = 'MODERATE';
        riskFactors = ['Mercury retrograde effects', 'Lunar node transitions', 'Planetary aspect patterns'];
    } else {
        riskLevel = 'LOW';
        riskFactors = ['Favorable planetary positions', 'Jupiter protection', 'Benevolent lunar phase'];
    }
    
    return {
        vrs_score: Math.round(vrsScore),
        risk_level: riskLevel,
        risk_factors: riskFactors,
        analysis: `Vedic astrological analysis indicates ${riskLevel.toLowerCase()} cyclone risk based on current planetary positions and location coordinates.`
    };
}

function generateMockCombinedResults(detection, astrology) {
    const aiRisk = detection.ai_risk_score;
    const astrologyRisk = astrology.vrs_score;
    const combinedRisk = Math.round((aiRisk + astrologyRisk) / 2);
    
    let finalRiskLevel, actionRequired, recommendations;
    
    if (combinedRisk >= 70) {
        finalRiskLevel = 'EXTREME';
        actionRequired = 'Immediate evacuation and emergency response required';
        recommendations = [
            '🚨 IMMEDIATE EVACUATION of coastal areas',
            '🆘 Activate emergency response protocols',
            '📡 Issue highest level weather warnings',
            '🏥 Prepare emergency medical facilities',
            '🚁 Deploy rescue and relief teams'
        ];
    } else if (combinedRisk >= 50) {
        finalRiskLevel = 'HIGH';
        actionRequired = 'High alert - prepare for severe weather conditions';
        recommendations = [
            '⚠️ Issue high-level weather alerts',
            '🏠 Prepare evacuation plans',
            '📻 Activate emergency communication systems',
            '🚒 Pre-position emergency response teams',
            '🏥 Alert medical facilities'
        ];
    } else if (combinedRisk >= 30) {
        finalRiskLevel = 'MODERATE';
        actionRequired = 'Moderate risk - maintain preparedness and monitor conditions';
        recommendations = [
            '📢 Issue weather advisories',
            '🏠 Review evacuation procedures',
            '📡 Monitor weather conditions closely',
            '🚒 Prepare emergency response teams',
            '📱 Keep public informed of developments'
        ];
    } else {
        finalRiskLevel = 'LOW';
        actionRequired = 'Low risk - standard monitoring recommended';
        recommendations = [
            '📊 Continue standard weather monitoring',
            '📱 Maintain public awareness programs',
            '🏠 Regular preparedness reviews',
            '📡 Monitor satellite imagery',
            '📋 Document conditions for future reference'
        ];
    }
    
    return {
        combined_risk_score: combinedRisk,
        final_risk_level: finalRiskLevel,
        action_required: actionRequired,
        recommendations: recommendations,
        confidence: detection.total_cyclones > 0 ? 'High' : 'Medium'
    };
}

function displayRealResults(apiResponse) {
    // Extract results from API response
    const results = apiResponse.results;
    console.log('🔍 Debug: Full API Response:', apiResponse);
    console.log('🔍 Debug: Results structure:', results);
    
    // Deep debug - log all possible detection-related paths
    console.log('🔍 Debug: results.detection:', results.detection);
    console.log('🔍 Debug: results.yolo_detection:', results.yolo_detection);
    console.log('🔍 Debug: results.enhanced_meteorological:', results.enhanced_meteorological);
    
    // If enhanced_meteorological exists, explore its structure
    if (results.enhanced_meteorological) {
        console.log('🔍 Debug: enhanced_meteorological.overall_assessment:', results.enhanced_meteorological.overall_assessment);
        console.log('🔍 Debug: enhanced_meteorological.detection_summary:', results.enhanced_meteorological.detection_summary);
        if (results.enhanced_meteorological.overall_assessment) {
            console.log('🔍 Debug: overall_assessment.detection_summary:', results.enhanced_meteorological.overall_assessment.detection_summary);
        }
    }
    
    // Function to safely extract nested values
    const safeGet = (obj, path) => {
        return path.split('.').reduce((current, key) => current && current[key], obj);
    };
    
    // Display AI Detection Results - handle multiple possible structures
    const detection = results.detection || results.yolo_detection || {};
    
    // Try to find total cyclones in various locations
    let totalCyclones = detection.total_cyclones || 
        safeGet(results, 'enhanced_meteorological.overall_assessment.detection_summary.total_cyclones') ||
        safeGet(results, 'enhanced_meteorological.detection_summary.total_cyclones') ||
        (detection.detections ? detection.detections.length : 0) ||
        (results.yolo_detection && results.yolo_detection.detections ? results.yolo_detection.detections.length : 0) ||
        0;
    
    // Additional fallback: count detections from enhanced analysis if available
    if (totalCyclones === 0 && results.enhanced_meteorological) {
        const enhancedDetections = safeGet(results, 'enhanced_meteorological.yolo_detections') ||
            safeGet(results, 'enhanced_meteorological.detections');
        if (enhancedDetections && Array.isArray(enhancedDetections)) {
            totalCyclones = enhancedDetections.length;
        }
    }
    
    // Try to find average confidence in various locations    
    let avgConfidence = detection.avg_confidence || 
        safeGet(results, 'enhanced_meteorological.overall_assessment.detection_summary.avg_yolo_confidence') ||
        safeGet(results, 'enhanced_meteorological.detection_summary.avg_yolo_confidence') ||
        0;
    
    // If no average confidence found, calculate from detections array
    if (avgConfidence === 0) {
        let detectionsArray = detection.detections || 
            (results.yolo_detection && results.yolo_detection.detections) ||
            safeGet(results, 'enhanced_meteorological.yolo_detections') ||
            safeGet(results, 'enhanced_meteorological.detections');
        
        if (detectionsArray && Array.isArray(detectionsArray) && detectionsArray.length > 0) {
            const confidenceSum = detectionsArray.reduce((sum, det) => {
                return sum + (det.confidence || det.score || 0);
            }, 0);
            avgConfidence = confidenceSum / detectionsArray.length;
        }
    }
    
    console.log('🔍 Debug: Total cyclones found:', totalCyclones);
    console.log('🔍 Debug: Avg confidence found:', avgConfidence);
        
    document.getElementById('cyclonesCount').textContent = totalCyclones;
    document.getElementById('avgConfidence').textContent = `${Math.round(avgConfidence * 100)}%`;
    
    // AI risk score may be under various locations
    const aiRiskScoreVal = (results.combined && results.combined.ai_detection && results.combined.ai_detection.ai_risk_score)
        || (results.combined_enhanced && results.combined_enhanced.combined_assessment && results.combined_enhanced.combined_assessment.ai_detection && results.combined_enhanced.combined_assessment.ai_detection.ai_risk_score)
        || (results.combined_enhanced && results.combined_enhanced.ai_risk_score)
        || 0;
    document.getElementById('aiRiskScore').textContent = aiRiskScoreVal;
    
    // Display Astrology Results
    const astrology = results.astrology.vrs_analysis;
    document.getElementById('vrsScore').textContent = `${astrology.vrs_score}/100`;
    const astrologyRiskElement = document.getElementById('astrologyRisk');
    astrologyRiskElement.textContent = astrology.risk_level;
    astrologyRiskElement.className = `metric-value risk-badge ${astrology.risk_level}`;
    
    // Display Risk Factors
    const riskFactorsContainer = document.getElementById('riskFactors');
    riskFactorsContainer.innerHTML = '';
    if (astrology.risk_factors && astrology.risk_factors.length > 0) {
        astrology.risk_factors.forEach(factor => {
            const factorElement = document.createElement('div');
            factorElement.className = 'risk-factor';
            factorElement.textContent = factor;
            riskFactorsContainer.appendChild(factorElement);
        });
    } else {
        const noFactorsElement = document.createElement('div');
        noFactorsElement.className = 'risk-factor';
        noFactorsElement.textContent = 'No significant risk factors detected';
        riskFactorsContainer.appendChild(noFactorsElement);
    }
    
    // Display Combined Assessment
    const combined = results.combined.combined_assessment;
    document.getElementById('combinedRiskScore').textContent = Math.round(combined.combined_risk_score);
    const finalRiskElement = document.getElementById('finalRiskLevel');
    finalRiskElement.textContent = combined.final_risk_level;
    finalRiskElement.className = `final-risk-level ${combined.final_risk_level}`;
    document.getElementById('actionText').textContent = combined.action_required;
    
    // Update risk circle color based on score
    updateRiskCircleColor(combined.combined_risk_score);
    
    // Display Recommendations
    const recommendationsContainer = document.getElementById('recommendationsList');
    recommendationsContainer.innerHTML = '';
    if (results.combined.recommendations) {
        results.combined.recommendations.forEach(recommendation => {
            const recElement = document.createElement('div');
            recElement.className = 'recommendation';
            recElement.innerHTML = `<div class="recommendation-text">${recommendation}</div>`;
            recommendationsContainer.appendChild(recElement);
        });
    }
    
    // Show results section
    showResultsSection();
    
    // Add animations
    setTimeout(() => {
        document.querySelectorAll('.result-card').forEach((card, index) => {
            setTimeout(() => {
                card.classList.add('slide-up');
            }, index * 100);
        });
    }, 100);
}

function displayEnhancedResults(apiResponse) {
    console.log('🧠 Displaying enhanced analysis results...');
    
    // First display regular results
    displayRealResults(apiResponse);
    
    // Extract enhanced results from API response
    const results = apiResponse.results;
    const enhanced = results.combined_enhanced;
    
    if (!enhanced) {
        console.warn('⚠️ No enhanced results found in API response');
        return;
    }
    
    // Show enhanced results card
    const enhancedCard = document.getElementById('enhancedResultsCard');
    enhancedCard.classList.remove('hidden');
    
    // Display Enhanced Meteorological Results
    if (enhanced.intensity_analysis) {
        const intensity = enhanced.intensity_analysis;
        
        // Intensity Classification
        const intensityElement = document.getElementById('intensityClassification');
        intensityElement.textContent = intensity.predicted_category || 'Unknown';
        intensityElement.className = `metric-value intensity-badge ${(intensity.predicted_category || '').toLowerCase().replace(' ', '-')}`;
        
        // ML Confidence
        const mlConfidenceElement = document.getElementById('mlConfidence');
        mlConfidenceElement.textContent = intensity.confidence ? `${Math.round(intensity.confidence * 100)}%` : '0%';
    }
    
    if (enhanced.eye_analysis) {
        const eye = enhanced.eye_analysis;
        
        // Eye Detection
        const eyeElement = document.getElementById('eyeDetection');
        eyeElement.textContent = eye.eye_detected ? 'Detected' : 'Not Detected';
        eyeElement.className = `metric-value eye-badge ${eye.eye_detected ? 'detected' : 'not-detected'}`;
        
        // Eye Clarity
        const clarityElement = document.getElementById('eyeClarity');
        clarityElement.textContent = eye.clarity_score ? `${Math.round(eye.clarity_score * 100)}%` : '0%';
    }
    
    if (enhanced.meteorological_features) {
        const features = enhanced.meteorological_features;
        
        // Structural Organization
        const organizationElement = document.getElementById('structuralOrganization');
        organizationElement.textContent = features.structural_organization || 'Unknown';
        
        // Development Stage
        const stageElement = document.getElementById('developmentStage');
        stageElement.textContent = features.development_stage || 'Unknown';
    }
    
    // Update assessment title for enhanced mode
    document.getElementById('combinedAssessmentTitle').textContent = 'Enhanced Combined Assessment';
    
    console.log('✅ Enhanced results displayed successfully');
}

function displayResults(results) {
    // Keep the old mock function for fallback
    // Display AI Detection Results
    document.getElementById('cyclonesCount').textContent = results.detection.total_cyclones;
    document.getElementById('avgConfidence').textContent = `${Math.round(results.detection.avg_confidence * 100)}%`;
    document.getElementById('aiRiskScore').textContent = results.detection.ai_risk_score;
    
    // Display Astrology Results
    document.getElementById('vrsScore').textContent = `${results.astrology.vrs_score}/100`;
    const astrologyRiskElement = document.getElementById('astrologyRisk');
    astrologyRiskElement.textContent = results.astrology.risk_level;
    astrologyRiskElement.className = `metric-value risk-badge ${results.astrology.risk_level}`;
    
    // Display Risk Factors
    const riskFactorsContainer = document.getElementById('riskFactors');
    riskFactorsContainer.innerHTML = '';
    results.astrology.risk_factors.forEach(factor => {
        const factorElement = document.createElement('div');
        factorElement.className = 'risk-factor';
        factorElement.textContent = factor;
        riskFactorsContainer.appendChild(factorElement);
    });
    
    // Display Combined Assessment
    document.getElementById('combinedRiskScore').textContent = results.combined.combined_risk_score;
    const finalRiskElement = document.getElementById('finalRiskLevel');
    finalRiskElement.textContent = results.combined.final_risk_level;
    finalRiskElement.className = `final-risk-level ${results.combined.final_risk_level}`;
    document.getElementById('actionText').textContent = results.combined.action_required;
    
    // Update risk circle color based on score
    updateRiskCircleColor(results.combined.combined_risk_score);
    
    // Display Recommendations
    const recommendationsContainer = document.getElementById('recommendationsList');
    recommendationsContainer.innerHTML = '';
    results.combined.recommendations.forEach(recommendation => {
        const recElement = document.createElement('div');
        recElement.className = 'recommendation';
        recElement.innerHTML = `<div class="recommendation-text">${recommendation}</div>`;
        recommendationsContainer.appendChild(recElement);
    });
    
    // Show results section
    showResultsSection();
    
    // Add animations
    setTimeout(() => {
        document.querySelectorAll('.result-card').forEach((card, index) => {
            setTimeout(() => {
                card.classList.add('slide-up');
            }, index * 100);
        });
    }, 100);
}

function updateRiskCircleColor(score) {
    const riskCircle = document.querySelector('.risk-circle');
    let gradient;
    
    if (score >= 70) {
        gradient = 'linear-gradient(135deg, #e74c3c 0%, #c0392b 100%)'; // Red
    } else if (score >= 50) {
        gradient = 'linear-gradient(135deg, #f39c12 0%, #e67e22 100%)'; // Orange
    } else if (score >= 30) {
        gradient = 'linear-gradient(135deg, #f1c40f 0%, #f39c12 100%)'; // Yellow
    } else {
        gradient = 'linear-gradient(135deg, #27ae60 0%, #2ecc71 100%)'; // Green
    }
    
    riskCircle.style.background = gradient;
}

function setupLoadingAnimation() {
    // This function can be expanded for more complex loading animations
}

function hideAllSections() {
    loadingSection.classList.add('hidden');
    resultsSection.classList.add('hidden');
    errorSection.classList.add('hidden');
}

function showLoadingSection(isEnhanced = false) {
    hideAllSections();
    loadingSection.classList.remove('hidden');
    loadingSection.classList.add('fade-in');
    
    // Show appropriate loading steps
    if (isEnhanced) {
        loadingSteps.classList.add('hidden');
        enhancedLoadingSteps.classList.remove('hidden');
    } else {
        loadingSteps.classList.remove('hidden');
        enhancedLoadingSteps.classList.add('hidden');
    }
}

function hideLoadingSection() {
    loadingSection.classList.add('hidden');
}

function showResultsSection() {
    hideAllSections();
    resultsSection.classList.remove('hidden');
    resultsSection.classList.add('fade-in');
}

function showError(message) {
    hideAllSections();
    document.getElementById('errorMessage').innerHTML = `<p>${message}</p>`;
    errorSection.classList.remove('hidden');
    errorSection.classList.add('fade-in');
}

// Utility Functions
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function getLocationName(latitude, longitude) {
    // This would typically call a geocoding API
    // For now, return a mock location name
    if (Math.abs(latitude - 19.0760) < 1 && Math.abs(longitude - 72.8777) < 1) {
        return 'Mumbai, India';
    } else if (Math.abs(latitude - 28.6139) < 1 && Math.abs(longitude - 77.2090) < 1) {
        return 'New Delhi, India';
    } else {
        return `${latitude.toFixed(2)}°, ${longitude.toFixed(2)}°`;
    }
}

// Export functions for potential backend integration
window.AstroAlert = {
    performAnalysis,
    displayResults,
    showError,
    hideAllSections
};

// Add some interactive features
document.addEventListener('DOMContentLoaded', function() {
    // Add ripple effect to buttons
    const buttons = document.querySelectorAll('.submit-btn');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 1000);
        });
    });
    
    // Add hover effects to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-4px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
});

// Add CSS for ripple effect
const rippleCSS = `
.ripple {
    position: absolute;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.5);
    transform: scale(0);
    animation: ripple 1s linear;
    pointer-events: none;
}

@keyframes ripple {
    to {
        transform: scale(2);
        opacity: 0;
    }
}
`;

// Inject ripple CSS
const style = document.createElement('style');
style.textContent = rippleCSS;
document.head.appendChild(style);

// ==========================================
// CHATBOT FUNCTIONALITY
// ==========================================

// Chatbot DOM elements
const chatbotContainer = document.getElementById('chatbotContainer');
const chatbotHeader = document.getElementById('chatbotHeader');
const chatbotToggle = document.getElementById('chatbotToggle');
const chatbotToggleIcon = document.getElementById('chatbotToggleIcon');
const chatbotStatus = document.getElementById('chatbotStatus');
const clearChatBtn = document.getElementById('clearChatBtn');
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendChatBtn = document.getElementById('sendChatBtn');
const charCount = document.getElementById('charCount');
const chatInputStatus = document.getElementById('chatInputStatus');
const suggestionsList = document.getElementById('suggestionsList');

// Chatbot state
let chatbotMinimized = true;
let chatbotAvailable = false;
let isTyping = false;

// Initialize chatbot
document.addEventListener('DOMContentLoaded', function() {
    initializeChatbot();
});

async function initializeChatbot() {
    // Set initial state
    chatbotContainer.classList.add('minimized');
    
    // Add event listeners
    chatbotHeader.addEventListener('click', toggleChatbot);
    chatbotToggle.addEventListener('click', (e) => {
        e.stopPropagation();
        toggleChatbot();
    });
    
    clearChatBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        clearChatHistory();
    });
    
    chatInput.addEventListener('input', updateCharCount);
    chatInput.addEventListener('keypress', handleChatInputKeypress);
    sendChatBtn.addEventListener('click', sendMessage);
    
    // Check chatbot availability
    await checkChatbotStatus();
    
    // Load suggested questions
    await loadSuggestedQuestions();
}

async function checkChatbotStatus() {
    try {
        const response = await fetch('/api/chat/status');
        const data = await response.json();
        
        chatbotAvailable = data.available;
        
        if (data.available) {
            chatbotStatus.textContent = 'Online • Ready to help!';
            chatbotStatus.style.color = '#27ae60';
            chatInputStatus.textContent = 'Ready';
            chatInputStatus.className = 'chat-status ready';
            
            console.log('🤖 CycloneBot is online!');
        } else {
            chatbotStatus.textContent = 'Offline • Check configuration';
            chatbotStatus.style.color = '#e74c3c';
            chatInputStatus.textContent = 'Unavailable';
            chatInputStatus.className = 'chat-status error';
            
            // Disable chat input
            chatInput.disabled = true;
            sendChatBtn.disabled = true;
            
            console.log('🤖 CycloneBot is offline:', data.message);
        }
    } catch (error) {
        console.error('Error checking chatbot status:', error);
        chatbotStatus.textContent = 'Connection Error';
        chatbotStatus.style.color = '#e74c3c';
        chatInputStatus.textContent = 'Error';
        chatInputStatus.className = 'chat-status error';
        
        chatInput.disabled = true;
        sendChatBtn.disabled = true;
    }
}

function toggleChatbot() {
    chatbotMinimized = !chatbotMinimized;
    
    if (chatbotMinimized) {
        chatbotContainer.classList.add('minimized');
        chatbotToggleIcon.textContent = '💬';
    } else {
        chatbotContainer.classList.remove('minimized');
        chatbotToggleIcon.textContent = '🔽';
        
        // Focus on chat input when opened
        setTimeout(() => {
            if (!chatInput.disabled) {
                chatInput.focus();
            }
        }, 300);
    }
}

function updateCharCount() {
    const currentLength = chatInput.value.length;
    charCount.textContent = `${currentLength}/500`;
    
    if (currentLength > 450) {
        charCount.style.color = '#e74c3c';
    } else if (currentLength > 350) {
        charCount.style.color = '#f39c12';
    } else {
        charCount.style.color = '#7f8c8d';
    }
}

function handleChatInputKeypress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

async function sendMessage() {
    const message = chatInput.value.trim();
    
    if (!message || !chatbotAvailable || isTyping) {
        return;
    }
    
    // Add user message to chat
    addMessage(message, 'user');
    
    // Clear input
    chatInput.value = '';
    updateCharCount();
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        });
        
        const data = await response.json();
        
        // Hide typing indicator
        hideTypingIndicator();
        
        if (data.success) {
            addMessage(data.response, 'bot', data.category);
            
            // Update suggested questions after getting response
            await loadSuggestedQuestions();
        } else {
            addMessage('Sorry, I encountered an error. Please try again.', 'bot', 'error');
        }
        
    } catch (error) {
        console.error('Chat error:', error);
        hideTypingIndicator();
        addMessage('Connection error. Please check your internet connection and try again.', 'bot', 'error');
    }
}

function addMessage(content, sender, category = 'general') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message ${category}`;
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    // Handle multi-paragraph content
    const paragraphs = content.split('\n\n').filter(p => p.trim());
    if (paragraphs.length > 1) {
        paragraphs.forEach(paragraph => {
            const p = document.createElement('p');
            p.textContent = paragraph.trim();
            messageContent.appendChild(p);
        });
    } else {
        const p = document.createElement('p');
        p.textContent = content;
        messageContent.appendChild(p);
    }
    
    messageDiv.appendChild(messageContent);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Add animation
    messageDiv.style.opacity = '0';
    messageDiv.style.transform = 'translateY(10px)';
    
    setTimeout(() => {
        messageDiv.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        messageDiv.style.opacity = '1';
        messageDiv.style.transform = 'translateY(0)';
    }, 50);
}

function showTypingIndicator() {
    isTyping = true;
    
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot-message';
    typingDiv.id = 'typingIndicator';
    
    const typingContent = document.createElement('div');
    typingContent.className = 'message-content chatbot-typing';
    
    const typingDots = document.createElement('div');
    typingDots.className = 'typing-dots';
    
    for (let i = 0; i < 3; i++) {
        const dot = document.createElement('div');
        dot.className = 'typing-dot';
        typingDots.appendChild(dot);
    }
    
    typingContent.appendChild(typingDots);
    typingDiv.appendChild(typingContent);
    chatMessages.appendChild(typingDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Update status
    chatInputStatus.textContent = 'Bot is typing...';
    chatInputStatus.className = 'chat-status sending';
    
    // Disable input
    sendChatBtn.disabled = true;
}

function hideTypingIndicator() {
    isTyping = false;
    
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
    
    // Update status
    chatInputStatus.textContent = 'Ready';
    chatInputStatus.className = 'chat-status ready';
    
    // Enable input
    sendChatBtn.disabled = false;
}

async function clearChatHistory() {
    try {
        const response = await fetch('/api/chat/clear', {
            method: 'POST'
        });
        
        if (response.ok) {
            // Clear chat messages (keep welcome message)
            const welcomeMessage = chatMessages.querySelector('.welcome-message');
            chatMessages.innerHTML = '';
            if (welcomeMessage) {
                chatMessages.appendChild(welcomeMessage);
            }
            
            console.log('🗑️ Chat history cleared');
        }
    } catch (error) {
        console.error('Error clearing chat history:', error);
    }
}

async function loadSuggestedQuestions() {
    try {
        const response = await fetch('/api/chat/suggestions');
        const data = await response.json();
        
        if (data.success && data.suggestions) {
            displaySuggestions(data.suggestions);
        }
    } catch (error) {
        console.error('Error loading suggestions:', error);
        // Show default suggestions
        displaySuggestions([
            'What is a tropical cyclone?',
            'How should I prepare for a cyclone?',
            'What do the risk levels mean?',
            'How does the VRS score work?'
        ]);
    }
}

function displaySuggestions(suggestions) {
    suggestionsList.innerHTML = '';
    
    suggestions.forEach(suggestion => {
        const suggestionBtn = document.createElement('button');
        suggestionBtn.className = 'suggestion-item';
        suggestionBtn.textContent = suggestion;
        suggestionBtn.addEventListener('click', () => {
            if (!chatbotAvailable || isTyping) return;
            
            chatInput.value = suggestion;
            updateCharCount();
            
            if (!chatbotMinimized) {
                chatInput.focus();
            } else {
                // Auto-open chatbot and send message
                toggleChatbot();
                setTimeout(() => {
                    sendMessage();
                }, 300);
            }
        });
        
        suggestionsList.appendChild(suggestionBtn);
    });
}
