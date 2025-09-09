// AstroAlert Frontend JavaScript

// DOM Elements
const analysisForm = document.getElementById('analysisForm');
const imageUpload = document.getElementById('imageUpload');
const datetimeInput = document.getElementById('datetime');
const loadingSection = document.getElementById('loadingSection');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');
const previewImage = document.getElementById('previewImage');
const uploadText = document.querySelector('.upload-text');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Set current datetime as default
    const now = new Date();
    const localDateTime = new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
    datetimeInput.value = localDateTime;

    // Add event listeners
    analysisForm.addEventListener('submit', handleFormSubmission);
    imageUpload.addEventListener('change', handleImageUpload);

    // Add loading step animation
    setupLoadingAnimation();
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
        datetime: datetime
    });
}

async function performAnalysis(data) {
    try {
        hideAllSections();
        showLoadingSection();
        
        // Simulate analysis steps
        await simulateAnalysisSteps();
        
        // Generate mock results (in real implementation, this would call your Python backend)
        const results = await generateMockResults(data);
        
        hideLoadingSection();
        displayResults(results);
        
    } catch (error) {
        console.error('Analysis error:', error);
        hideLoadingSection();
        showError('An error occurred during analysis. Please try again.');
    }
}

async function simulateAnalysisSteps() {
    const steps = document.querySelectorAll('.step');
    
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

function displayResults(results) {
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

function showLoadingSection() {
    hideAllSections();
    loadingSection.classList.remove('hidden');
    loadingSection.classList.add('fade-in');
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
