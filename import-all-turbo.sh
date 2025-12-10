#!/bin/bash
# Auto-import all remaining wordlists

cd /home/mmi/kwiklabs/BreachVault

echo "════════════════════════════════════════════"
echo "  DATASEED MASTER-9000: Batch Import"
echo "════════════════════════════════════════════"
echo ""

# Import all wordlists in sequence
./turbo-import.py ~/Downloads/rockyou.txt rockyou
echo ""
echo "─────────────────────────────────────────────"
echo ""

./turbo-import.py ~/Downloads/crackstation.txt crackstation
echo ""
echo "─────────────────────────────────────────────"
echo ""

./turbo-import.py ~/Downloads/weakpass_4.txt weakpass_4
echo ""

echo "════════════════════════════════════════════"
echo "  🎉 ALL IMPORTS COMPLETE!"
echo "════════════════════════════════════════════"
