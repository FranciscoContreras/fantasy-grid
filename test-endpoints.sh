#!/bin/bash

# Fantasy Grid API Test Suite
# Tests all endpoints to verify Phase 5 deployment

BASE_URL="https://fantasy-grid-8e65f9ca9754.herokuapp.com"

echo "=========================================="
echo "Fantasy Grid API Test Suite"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# Helper function to test endpoint
test_endpoint() {
    local name=$1
    local url=$2
    local expected_status=${3:-200}

    echo -n "Testing: $name... "

    response=$(curl -s -w "\n%{http_code}" "$url")
    status_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | head -n -1)

    if [ "$status_code" -eq "$expected_status" ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $status_code)"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $status_code, expected $expected_status)"
        echo "Response: $body" | head -c 200
        echo ""
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# Test 1: Health Check
echo "=== Core Endpoints ==="
test_endpoint "Health Check" "$BASE_URL/health"

# Test 2: Player Search
test_endpoint "Player Search (Aaron)" "$BASE_URL/api/players/search?q=aaron"

# Test 3: Player Search with Position Filter
test_endpoint "Player Search (QB only)" "$BASE_URL/api/players/search?q=aaron&position=QB"

# Test 4: Get Specific Player
PLAYER_ID="b31ee0b9-858d-455f-b504-4e00479b0110"  # Aaron Rodgers
test_endpoint "Get Player Details" "$BASE_URL/api/players/$PLAYER_ID"

# Test 5: Player Career Stats
test_endpoint "Player Career Stats" "$BASE_URL/api/players/$PLAYER_ID/career"

# Test 6: Player Analysis History
test_endpoint "Player Analysis History" "$BASE_URL/api/players/$PLAYER_ID/history?limit=5"

# Test 7: Frontend Root
test_endpoint "Frontend Homepage" "$BASE_URL/"

# Test 8: Frontend Static Assets
test_endpoint "Frontend CSS" "$BASE_URL/assets/index-Da2C_Q3F.css"

echo ""
echo "=========================================="
echo "Test Results Summary"
echo "=========================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo "Total: $((PASSED + FAILED))"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed! ✓${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed ✗${NC}"
    exit 1
fi
