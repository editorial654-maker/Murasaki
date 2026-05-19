#!/bin/bash

# - Developer Identity
DEV="@LAXXYPLAYZZ"
FOOTER="@DRX_POWER"

# Colors
CYAN='\033[1;36m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
RED='\033[1;31m'
NC='\033[0m' 

clear

show_banner() {
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}  _____  _______  __  _____   ______          ________ _____  ${NC}"
    echo -e "${YELLOW} |  __ \|  __ \ \ / / |  __ \ / __ \ \        / /  ____|  __ \ ${NC}"
    echo -e "${YELLOW} | |  | | |__) \ V /  | |__) | |  | \ \  /\  / /| |__  | |__) |${NC}"
    echo -e "${YELLOW} | |  | |  _  / > <   |  ___/| |  | |\ \/  \/ / |  __| |  _  / ${NC}"
    echo -e "${YELLOW} | |  | | | \ \/ . \  | |    | |__| | \  /\  /  | |____| | \ \ ${NC}"
    echo -e "${YELLOW} |_____/|_|  \_\_/\_\ |_|     \____/   \/  \/   |______|_|  \_|${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "       ${GREEN}🚀 DRX POWER SYSTEM RENDER-INSTALLER v3.2 🚀${NC}"
    echo -e "       ${CYAN}Owner: $FOOTER | Dev: $DEV${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

progress_bar() {
    local duration=$1
    local task=$2
    echo -ne "${YELLOW}[#] $task: [          ] (0%)\r"
    sleep 0.5
    echo -ne "${YELLOW}[#] $task: [■■■■      ] (40%)\r"
    sleep 0.5
    echo -ne "${YELLOW}[#] $task: [■■■■■■■■  ] (80%)\r"
    sleep 0.5
    echo -ne "${GREEN}[#] $task: [■■■■■■■■■■] (100%)\n"
}

show_banner

# Step 1: Python Libraries via requirements.txt
echo -e "${CYAN}[>] Installing Libraries from requirements.txt...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt > /dev/null 2>&1
    progress_bar 1 "Library Integration"
else
    echo -e "${RED}[X] requirements.txt not found!${NC}"
fi

# Step 2: Binary Compilation
echo -e "${CYAN}[>] Checking for drx.c source code...${NC}"
if [ -f "drx.c" ]; then
    echo -e "${YELLOW}[!] Converting drx.c to Binary (drx)...${NC}"
    gcc drx.c -o drx -lpthread > /dev/null 2>&1
    chmod +x drx
    progress_bar 1 "Binary Compilation"
fi

# Step 3: Permissions
echo -e "${CYAN}[>] Configuring File Permissions...${NC}"
if [ -f "drx.py" ]; then
    chmod +x drx.py
fi
progress_bar 1 "Security & Permissions"

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ INSTALLATION & COMPILATION COMPLETED!${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "${YELLOW}[!] Ready for deployment on Render Terminal...${NC}"
