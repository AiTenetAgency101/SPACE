#!/bin/bash

# ============================================================================
# ENGINE2 DHI Migration - Build Validation Script
# This script validates all Dockerfiles and docker-compose configurations
# ============================================================================

set -e

echo "==============================================="
echo "ENGINE2 DHI Migration - Build Validation"
echo "==============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

FAILED=0
PASSED=0

# Function to test Dockerfile syntax
test_dockerfile() {
    local dockerfile=$1
    local context=$2
    local service=$3
    
    echo -n "Testing $service... "
    
    if docker buildx build -f "$dockerfile" "$context" --progress=plain --dry-run 2>/dev/null | grep -q "STEP"; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((FAILED++))
    fi
}

# Function to validate docker-compose syntax
test_compose() {
    local compose_file=$1
    local compose_name=$2
    
    echo -n "Testing $compose_name... "
    
    if docker-compose -f "$compose_file" config >/dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((FAILED++))
    fi
}

# Test Dockerfiles
echo "========== DOCKERFILE VALIDATION =========="
echo ""

cd "TruthFirst-Genesis/ENGINE2"

test_dockerfile "Dockerfile.optimized" "." "Dockerfile.optimized"
test_dockerfile "tenetaiagency-101/Dockerfile" "tenetaiagency-101" "tenetaiagency-101"
test_dockerfile "ultimate-engine/Dockerfile" "ultimate-engine" "ultimate-engine"
test_dockerfile "engine-365-days/Dockerfile" "engine-365-days" "engine-365-days"
test_dockerfile "restricted-aichatbot-trader/Dockerfile" "restricted-aichatbot-trader" "restricted-aichatbot-trader"

echo ""
echo "========== DOCKER-COMPOSE VALIDATION =========="
echo ""

test_compose "docker-compose-full-stack.yml" "docker-compose-full-stack.yml"
test_compose "docker-compose-production.yml" "docker-compose-production.yml"
test_compose "docker-compose-minimal.yml" "docker-compose-minimal.yml"

echo ""
echo "========== BUILD SYNTAX CHECK =========="
echo ""

# Check for DHI image references
echo -n "Checking DHI image references... "
if grep -r "dhi.io/" . --include="*.yml" --include="Dockerfile*" >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Found DHI images${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ No DHI images found${NC}"
    ((FAILED++))
fi

# Check for non-root user configuration
echo -n "Checking non-root user configuration... "
if grep -r "USER " . --include="Dockerfile*" >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Found USER directives${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ Missing USER directives${NC}"
    ((FAILED++))
fi

# Check for multi-stage builds
echo -n "Checking multi-stage build patterns... "
if grep -r "FROM.*AS" . --include="Dockerfile*" >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Found multi-stage builds${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ Missing multi-stage builds${NC}"
    ((FAILED++))
fi

# Check for health checks
echo -n "Checking health check configuration... "
if grep -r "HEALTHCHECK" . --include="Dockerfile*" >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Found health checks${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ Missing health checks${NC}"
    ((FAILED++))
fi

# Check for non-privileged ports
echo -n "Checking non-privileged port configuration... "
if grep -r "EXPOSE [1-9][0-9][0-9][0-9]" . --include="Dockerfile*" >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Using non-privileged ports${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠ Check ports manually${NC}"
fi

echo ""
echo "========== VALIDATION SUMMARY =========="
echo ""
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ All validations passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Build images: docker-compose -f docker-compose-production.yml build"
    echo "2. Push to registry: docker push <image>:<tag>"
    echo "3. Deploy: docker-compose up -d"
    echo "4. Scan for CVEs: trivy image <image>:<tag>"
    exit 0
else
    echo ""
    echo -e "${RED}✗ Some validations failed. Please review the issues above.${NC}"
    exit 1
fi
