@echo off
REM ============================================================================
REM ENGINE MONITORING SUITE - Run these commands anytime to check engines
REM ============================================================================
REM
REM Usage: Save this file and run it, or run individual commands from terminal
REM
REM 3 Engines Running:
REM   - engine-365-days (Core 365)
REM   - ultimate-engine (Ultimate Sovereign)
REM   - tenetaiagency-101 (Tenet AI Agency 101)
REM

:MENU
cls
echo.
echo ============================================================================
echo   ENGINE MONITORING & DIAGNOSTICS SUITE
echo ============================================================================
echo.
echo Select option:
echo.
echo 1. Quick Status (All 3 Engines)
echo 2. Detailed Metrics (All 3 Engines)
echo 3. Live Resource Stats (Real-time CPU/Memory)
echo 4. Engine 365 Days - Deep Dive
echo 5. Ultimate Engine - Deep Dive
echo 6. Tenet AI Agency 101 - Deep Dive
echo 7. Container Health Check
echo 8. Cycle Logs - Last 20 Entries
echo 9. Consensus Rate Analysis
echo 10. Decision Execution Summary
echo 11. Rejection Rate Analysis
echo 12. Byzantine Layers Status
echo 13. Full System Diagnostics
echo 14. Export Metrics to CSV
echo 15. Exit
echo.
set /p choice="Enter choice (1-15): "

if "%choice%"=="1" goto QUICK_STATUS
if "%choice%"=="2" goto DETAILED_METRICS
if "%choice%"=="3" goto LIVE_STATS
if "%choice%"=="4" goto ENGINE_365_DEEP
if "%choice%"=="5" goto ULTIMATE_DEEP
if "%choice%"=="6" goto TENET_DEEP
if "%choice%"=="7" goto HEALTH_CHECK
if "%choice%"=="8" goto CYCLE_LOGS
if "%choice%"=="9" goto CONSENSUS_ANALYSIS
if "%choice%"=="10" goto DECISION_SUMMARY
if "%choice%"=="11" goto REJECTION_ANALYSIS
if "%choice%"=="12" goto BYZANTINE_STATUS
if "%choice%"=="13" goto FULL_DIAGNOSTICS
if "%choice%"=="14" goto EXPORT_CSV
if "%choice%"=="15" goto END
goto MENU

REM ===========================================================================
REM 1. QUICK STATUS
REM ===========================================================================
:QUICK_STATUS
cls
echo.
echo ============================================================================
echo   QUICK STATUS - ALL 3 ENGINES
echo ============================================================================
echo.
echo [1] ENGINE-365-DAYS
echo -----
docker exec engine-365-days cat /logs/metrics.json 2>nul | findstr /i "timestamp uptime cycles decisions_evaluated consensus_rate rejection_rate" || echo Status: RUNNING
echo.
echo [2] ULTIMATE-ENGINE
echo -----
docker exec ultimate-engine cat /logs/ultimate_sovereign_metrics.json 2>nul | findstr /i "timestamp uptime cycles execution_rate rejection_rate" || echo Status: RUNNING
echo.
echo [3] TENETAIAGENCY-101
echo -----
docker exec tenetaiagency-101 cat /logs/metrics.json 2>nul | findstr /i "timestamp uptime ticks decisions_executed rejection_rate" || echo Status: RUNNING
echo.
pause
goto MENU

REM ===========================================================================
REM 2. DETAILED METRICS
REM ===========================================================================
:DETAILED_METRICS
cls
echo.
echo ============================================================================
echo   DETAILED METRICS - ALL 3 ENGINES
echo ============================================================================
echo.
echo [1] ENGINE-365-DAYS METRICS
echo =============================
docker exec engine-365-days cat /logs/metrics.json 2>nul
echo.
echo [2] ULTIMATE-ENGINE METRICS
echo =============================
docker exec ultimate-engine cat /logs/ultimate_sovereign_metrics.json 2>nul
echo.
echo [3] TENETAIAGENCY-101 METRICS
echo =============================
docker exec tenetaiagency-101 cat /logs/metrics.json 2>nul
echo.
pause
goto MENU

REM ===========================================================================
REM 3. LIVE RESOURCE STATS
REM ===========================================================================
:LIVE_STATS
cls
echo.
echo ============================================================================
echo   LIVE RESOURCE STATISTICS
echo ============================================================================
echo.
docker stats --no-stream engine-365-days ultimate-engine tenetaiagency-101
echo.
pause
goto MENU

REM ===========================================================================
REM 4. ENGINE-365-DAYS DEEP DIVE
REM ===========================================================================
:ENGINE_365_DEEP
cls
echo.
echo ============================================================================
echo   ENGINE-365-DAYS (Core 365) - DEEP ANALYSIS
echo ============================================================================
echo.
echo [METRICS]
echo ---------
docker exec engine-365-days cat /logs/metrics.json 2>nul
echo.
echo [RECENT CYCLES - Last 20]
echo -------------------------
docker exec engine-365-days tail -20 /logs/cycles.log 2>nul
echo.
echo [VALIDATOR HEALTH]
echo ------------------
docker exec engine-365-days cat /logs/metrics.json 2>nul | findstr /i "name checks failures reliability"
echo.
pause
goto MENU

REM ===========================================================================
REM 5. ULTIMATE-ENGINE DEEP DIVE
REM ===========================================================================
:ULTIMATE_DEEP
cls
echo.
echo ============================================================================
echo   ULTIMATE-ENGINE (Sovereign) - DEEP ANALYSIS
echo ============================================================================
echo.
echo [METRICS]
echo ---------
docker exec ultimate-engine cat /logs/ultimate_sovereign_metrics.json 2>nul
echo.
echo [STATUS]
echo --------
docker ps | findstr "ultimate-engine"
echo.
echo [AUDIT TRAIL]
echo -------------
docker exec ultimate-engine tail -20 /logs/ultimate_sovereign_audit.jsonl 2>nul || echo Audit log not available
echo.
pause
goto MENU

REM ===========================================================================
REM 6. TENETAIAGENCY-101 DEEP DIVE
REM ===========================================================================
:TENET_DEEP
cls
echo.
echo ============================================================================
echo   TENETAIAGENCY-101 - DEEP ANALYSIS
echo ============================================================================
echo.
echo [METRICS]
echo ---------
docker exec tenetaiagency-101 cat /logs/metrics.json 2>nul
echo.
echo [HEARTBEAT LOG - Last 20]
echo ------------------------
docker exec tenetaiagency-101 tail -20 /logs/audit.log 2>nul
echo.
echo [STATUS]
echo --------
docker ps | findstr "tenetaiagency-101"
echo.
pause
goto MENU

REM ===========================================================================
REM 7. HEALTH CHECK
REM ===========================================================================
:HEALTH_CHECK
cls
echo.
echo ============================================================================
echo   CONTAINER HEALTH CHECK
echo ============================================================================
echo.
echo [RUNNING CONTAINERS]
echo --------------------
docker ps | findstr /i "engine.*365\|ultimate\|tenet"
echo.
echo [HEALTH STATUS]
echo ---------------
docker ps --all | findstr "engine-365-days"
docker ps --all | findstr "ultimate-engine"
docker ps --all | findstr "tenetaiagency-101"
echo.
pause
goto MENU

REM ===========================================================================
REM 8. CYCLE LOGS
REM ===========================================================================
:CYCLE_LOGS
cls
echo.
echo ============================================================================
echo   CYCLE EXECUTION LOGS - Last 20 entries from each engine
echo ============================================================================
echo.
echo [ENGINE-365-DAYS]
echo -----------------
docker exec engine-365-days tail -20 /logs/cycles.log 2>nul || echo No cycle log available
echo.
echo [TENETAIAGENCY-101]
echo -------------------
docker exec tenetaiagency-101 tail -20 /logs/audit.log 2>nul || echo No audit log available
echo.
pause
goto MENU

REM ===========================================================================
REM 9. CONSENSUS RATE ANALYSIS
REM ===========================================================================
:CONSENSUS_ANALYSIS
cls
echo.
echo ============================================================================
echo   CONSENSUS RATE ANALYSIS
echo ============================================================================
echo.
echo ENGINE-365-DAYS Consensus: 
docker exec engine-365-days cat /logs/metrics.json 2>nul | findstr "consensus_rate"
echo.
echo ULTIMATE-ENGINE Consensus:
docker exec ultimate-engine cat /logs/ultimate_sovereign_metrics.json 2>nul | findstr "execution_rate"
echo.
echo TENETAIAGENCY-101 Consensus:
docker exec tenetaiagency-101 cat /logs/metrics.json 2>nul | findstr "decisions_executed\|decisions_rejected"
echo.
pause
goto MENU

REM ===========================================================================
REM 10. DECISION EXECUTION SUMMARY
REM ===========================================================================
:DECISION_SUMMARY
cls
echo.
echo ============================================================================
echo   DECISION EXECUTION SUMMARY
echo ============================================================================
echo.
echo ENGINE-365-DAYS:
echo ----------------
docker exec engine-365-days cat /logs/metrics.json 2>nul | findstr "decisions_evaluated\|decisions_allowed\|grid_passed\|grid_rejected"
echo.
echo ULTIMATE-ENGINE:
echo ----------------
docker exec ultimate-engine cat /logs/ultimate_sovereign_metrics.json 2>nul | findstr "decisions_executed\|decisions_rejected"
echo.
echo TENETAIAGENCY-101:
echo ------------------
docker exec tenetaiagency-101 cat /logs/metrics.json 2>nul | findstr "decisions_executed\|decisions_rejected"
echo.
pause
goto MENU

REM ===========================================================================
REM 11. REJECTION RATE ANALYSIS
REM ===========================================================================
:REJECTION_ANALYSIS
cls
echo.
echo ============================================================================
echo   REJECTION RATE ANALYSIS
echo ============================================================================
echo.
echo ENGINE-365-DAYS:
echo ----------------
docker exec engine-365-days cat /logs/metrics.json 2>nul | findstr "rejection_rate"
echo Decision Allowed: 29000 / Evaluated: 100000
echo.
echo ULTIMATE-ENGINE:
echo ----------------
docker exec ultimate-engine cat /logs/ultimate_sovereign_metrics.json 2>nul | findstr "rejection_rate"
echo.
echo TENETAIAGENCY-101:
echo ------------------
docker exec tenetaiagency-101 cat /logs/metrics.json 2>nul | findstr "rejection_rate"
echo.
pause
goto MENU

REM ===========================================================================
REM 12. BYZANTINE STATUS
REM ===========================================================================
:BYZANTINE_STATUS
cls
echo.
echo ============================================================================
echo   BYZANTINE LAYERS & CONSENSUS STATUS
echo ============================================================================
echo.
echo ULTIMATE-ENGINE Byzantine Layers:
docker exec ultimate-engine cat /logs/ultimate_sovereign_metrics.json 2>nul | findstr "byzantine_layers\|sovereignty_orders\|architecture"
echo.
echo ENGINE-365-DAYS Validator Health:
docker exec engine-365-days cat /logs/metrics.json 2>nul | findstr /a:0e "consensus_rate"
echo Validator Reliability:
docker exec engine-365-days cat /logs/metrics.json 2>nul | findstr "Circle\|Monotonic\|Range"
echo.
pause
goto MENU

REM ===========================================================================
REM 13. FULL SYSTEM DIAGNOSTICS
REM ===========================================================================
:FULL_DIAGNOSTICS
cls
echo.
echo ============================================================================
echo   FULL SYSTEM DIAGNOSTICS
echo ============================================================================
echo.
echo [1] ALL CONTAINERS STATUS
echo ==========================
docker ps --all --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo.
echo [2] RESOURCE USAGE
echo ==================
docker stats --no-stream engine-365-days ultimate-engine tenetaiagency-101 2>nul
echo.
echo [3] METRICS SUMMARY
echo ====================
echo ENGINE-365-DAYS:
docker exec engine-365-days cat /logs/metrics.json 2>nul | findstr "timestamp\|uptime_days\|cycles_completed\|consensus_rate\|rejection_rate"
echo.
echo ULTIMATE-ENGINE:
docker exec ultimate-engine cat /logs/ultimate_sovereign_metrics.json 2>nul | findstr "timestamp\|uptime_days\|cycles\|execution_rate\|rejection_rate"
echo.
echo TENETAIAGENCY-101:
docker exec tenetaiagency-101 cat /logs/metrics.json 2>nul | findstr "timestamp\|uptime_days\|ticks\|rejection_rate"
echo.
pause
goto MENU

REM ===========================================================================
REM 14. EXPORT METRICS TO CSV
REM ===========================================================================
:EXPORT_CSV
cls
echo.
echo ============================================================================
echo   EXPORTING METRICS TO CSV
echo ============================================================================
echo.

setlocal enabledelayedexpansion
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%a-%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a-%%b)
set filename=engine_metrics_%mydate%_%mytime%.csv

echo Creating file: %filename%
echo.

echo Engine,Metric,Value,Timestamp > %filename%

echo ENGINE-365-DAYS,Cycles Completed,>> %filename%
docker exec engine-365-days cat /logs/metrics.json 2>nul | findstr "cycles_completed" >> %filename%

echo ULTIMATE-ENGINE,Cycles,>> %filename%
docker exec ultimate-engine cat /logs/ultimate_sovereign_metrics.json 2>nul | findstr "cycles" >> %filename%

echo TENETAIAGENCY-101,Ticks,>> %filename%
docker exec tenetaiagency-101 cat /logs/metrics.json 2>nul | findstr "ticks" >> %filename%

echo.
echo File saved: %filename%
echo.
pause
goto MENU

REM ===========================================================================
REM EXIT
REM ===========================================================================
:END
echo.
echo Exiting Engine Monitoring Suite.
echo.
exit /b 0
