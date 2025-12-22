# Debugging Guide for Context Distraction Evaluation


## Debugging Workflow

### Step 1: Run Local Test
```bash
source .venv/bin/activate
python -m context_distraction.tests.test_graph
```

### Step 2: Fetch Latest Trace
```bash
python debug/dump_full_trace.py
```
This creates `full_trace.json` with the complete trace including all child runs.

### Step 3: Analyze Deliverables
Check what values were actually stored:
```bash
python debug/fetch_latest_trace.py | grep -A 20 "DELIVERABLES"
```

### Step 4: Inspect Specific Researcher
Use `debug/inspect_researcher.py` to examine what a specific researcher did:
- What tools were called
- What parameters were passed
- What results were returned

Example trace analysis:
```python
# Find researcher by deliverable key
for child in data['children']:
    if child.get('name') == 'researcher':
        dk = child.get('inputs', {}).get('deliverable_key', '')
        if 'NPV' in dk:
            # Analyze this researcher's tool calls
            pass
```

### Step 5: Check Researcher Inputs
Common issues to check:
1. **Are parameters reaching the researcher?**
   ```python
   inputs.get('data_level')  # Should NOT be None
   inputs.get('data_source')  # Should NOT be None
   inputs.get('calculation_guidance')  # Should NOT be None
   ```

2. **Are tool calls using correct values?**
   - Check if values match what tools returned
   - Look for unit conversion issues (millions vs dollars)
   - Look for manual array generation errors

3. **Did store_deliverable get called?**
   ```python
   # Search for store_deliverable tool calls
   grep -A 5 '"name": "store_deliverable"' full_trace.json
   ```

---

## Common Error Patterns

### Pattern 1: "To be determined"
**Symptom:** Deliverable value is "To be determined" in final results

**Causes:**
- Researcher hit recursion limit
- Researcher couldn't find data
- store_deliverable was never called
- Parameter passing bug (check if guidance is None)

**Debug:** Check researcher's tool calls to see where it got stuck

---

### Pattern 2: Wrong Calculation Value
**Symptom:** Deliverable has a value but it's incorrect (e.g., 8255 instead of 108)

**Causes:**
- Units error (millions vs dollars)
- Wrong parameters passed to calculation tool
- Manual array generation error
- Using wrong tool result in next step

**Debug:**
1. Find the researcher's calculate_* tool call
2. Check the input parameters
3. Check if values came from previous tool results or were hallucinated

---

### Pattern 3: Array with "Infinity" or Wrong Values
**Symptom:** Array like `[15, 18, 21.6, ..., "Infinity", "Infinity"]` or `[..., 5377, 6452]`

**Causes:**
- LLM generating array mentally instead of using tools
- Arithmetic errors in mental calculation

**Fix:** Guidance to use atomic tools (calculate_power) for each element

---

## Key Files

### Instructions
- `context_distraction/instructions.py` - All agent instructions
  - `GRAPH_PLANNER_INSTRUCTIONS` - Extracts deliverables from query
  - `GRAPH_SUPERVISOR_INSTRUCTIONS` - Delegates to researchers
  - `GRAPH_RESEARCHER_INSTRUCTIONS` - **Most critical for accuracy**
  - `FINAL_REPORT_INSTRUCTIONS` - Generates final report

### State Management
- `context_distraction/state.py` - State schemas
  - `ResearcherState` - **Must include all parameters passed from supervisor**
  - `SupervisorState`

### Tools
- `context_distraction/tools.py`
  - `create_deep_research_tool()` - **Check parameter passing here** (line ~1407)
  - `store_deliverable` - Stores researcher results
  - Calculation tools (calculate_cost_benefit_analysis, etc.)

### Tests
- `context_distraction/tests/test_graph.py` - Graph agent test
- `context_distraction/tests/test_agent.py` - Standard agent test
- `context_distraction/tests/setup_datasets.py` - Dataset configuration

---

## Instruction Design Principles

### What Worked
1. **Explicit examples** - Showing "$100 million → 100" worked better than generic guidance
2. **Critical sections** - Using "CRITICAL:" prefix makes LLMs pay attention
3. **Numbered steps** - Breaking processes into clear steps improved following
4. **Concise but emphatic** - Short instructions with **bold emphasis** on key points

### What Didn't Work
1. **Overly verbose instructions** - LLMs skip long paragraphs
2. **Subtle suggestions** - "Prefer using tools" is too weak; "Use tools, not mental math" is better
3. **Repetition without emphasis** - Saying same thing 3 times doesn't help if not emphasized
4. **Abstract principles** - "Be systematic" is vague; specific 4-step process is better

---

## Testing Strategy

### Before Running Tests
1. Analyze what changed since last test
2. Predict what should improve
3. Identify what might break
4. **Always ask permission before running** (tests take several minutes)

### After Running Tests
1. Compare recall with previous run
2. Check Q1-Q5 specifically (target: consistently correct)
3. Identify which questions changed (improved/degraded)
4. Fetch trace for failed questions only

---

## Performance Optimization Tips

1. **Fix critical bugs first** - Parameter passing bug had massive impact
2. **Focus on Q1-Q5** - Get basics right before tackling complex questions
3. **One issue at a time** - Don't stack multiple changes without testing
4. **Units matter** - A 1000x multiplier error dominates everything else
5. **Trace is truth** - Don't guess, look at what actually happened

---

## Future Work

### Test Case 3: Quantum Computing (Temporarily Removed)
**Status**: Removed from demo notebook due to recursion issue

**Issue**: Graph agent hits recursion limit when running on Case 3 (Quantum Computing focus)
- Agent repeatedly calls `calculate_present_value` with similar parameters
- Gets stuck in calculation loop without making progress
- Eventually hits LangGraph recursion limit (200 steps)

**Performance before removal**:
- Recall Accuracy: 44.44% (4/9 correct)
- Tool Call Completeness: 56.25% (9/16 expected calls)
- Tool Call Efficiency: 0.00% (237 actual vs 16 expected - sign of issue)

**Next Steps**:
1. Investigate LangSmith traces for Case 3 to identify exact loop pattern
2. Determine if issue is specific to Quantum Computing domain or certain calculation types
3. Consider adding loop detection or calculation step limits
4. Re-test Case 3 in isolation before adding back to demo

*See Appendix A for full test case data*

### Remaining Issues (Q8, Q9)
- Q8: Market share percentage (24.99 vs 41.69) - Calculation or data source issue
- Q9: Weighted average NPV (868.84 vs 96.01) - Likely units or parameter issue

### Potential Improvements
1. Add validation to calculation tools (reject obviously wrong inputs)
2. Better error messages when tools fail
3. Researcher should verify its answer before storing
4. Supervisor could validate deliverable values (sanity checks)
5. Add loop detection for repeated atomic tool calls

---

## Quick Reference Commands

```bash
# Run test
python -m context_distraction.tests.test_graph

# Fetch latest trace
python debug/dump_full_trace.py

# Check deliverables
python debug/fetch_latest_trace.py | grep -A 20 "Deliverables:"

# Find specific researcher
grep -A 100 '"deliverable_key": "NPV"' full_trace.json

# Check tool calls
grep -A 5 '"name": "calculate_' full_trace.json | less

# Clean up
rm -f full_trace.json test_output.log
```

---

## Appendix A: Quantum Computing Test Case Data

### Test Case Definition
**Name**: Task 3: 5 Domains - Focus on Quantum Computing
**Primary Domain**: quantum_computing
**Secondary Domain**: artificial_intelligence
**All Domains**: renewable_energy, artificial_intelligence, electric_vehicles, quantum_computing, biotechnology

### Recall Questions (9 total)
1. What was the number of qubits for quantum computing? (Expected: 1121 qubits)
2. What is the global AI market size in billions of USD? (Expected: 196.6 billion)
3. What was the calculated 10-year compound growth final value for quantum computing? (Expected: 170.91)
4. What was the NPV calculated for quantum computing CBA with 10% discount rate? (Expected: 85.12)
5. What was the risk-adjusted NPV for quantum computing? (Expected: 34.05)
6. What is the weighted average growth rate across all domains, weighted by market size? (Expected: 0.143)
7. What is the discount factor for year 7 at 10% discount rate? (Expected: 0.513158)
8. What was the strategic priority ranking for quantum computing among all domains in your final analysis? (Expected: Rank 1)
9. What is the ratio of quantum computing NPV to artificial intelligence NPV (both at 10% discount)? (Expected: 0.669)

### Expected Tool Calls
- Statistics gathering: 6 calls
- Expert opinions: 4 calls
- Case studies: 3 calls
- Year data: 4 calls
- Comparisons: 2 calls

### Test Case Configuration
```python
{
    "stats_count": 6,
    "expert_count": 4,
    "case_count": 3,
    "year_count": 4,
    "compare_count": 2
}
```

### Last Known Results (Before Removal)
**Recall Accuracy**: 44.44% (4/9 correct)
- Q1: ✓ 1121 (correct)
- Q2: ✓ 196.6 (correct)
- Q3: ✗ 100.53 vs 170.91 expected
- Q4: ✗ 83.86 vs 85.12 expected
- Q5: ✗ 0.8 vs 34.05 expected
- Q6: ✗ 14.4039 vs 0.143 expected
- Q7: ✓ 0.513158 (correct)
- Q8: ✓ 1 (correct)
- Q9: ✗ 0.659 vs 0.669 expected

**Tool Call Metrics**:
- Completeness: 56.25% (9/16 expected calls found)
- Efficiency: 0.00% (237 actual vs 16 expected - massive excess)
- Missing expected tool call indices: [3, 7, 9, 10, 11, 13, 15]

### File Location
Original test case definition was at:
```
/context_distraction/resources/test_tasks.py (lines 178-225, now removed)
```
