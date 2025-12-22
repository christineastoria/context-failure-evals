# Debugging Guide for Context Distraction Evaluation

## Session Summary: Dec 21, 2024

**Starting Performance:** 33% recall (3/9 correct)
**Final Performance:** 78% recall (7/9 correct)
**Target:** 66% recall per test case

---

## Key Issues Found and Fixed

### 1. **Parameter Passing Bug**
**Problem:** Researcher agents received `None` for `data_level`, `data_source`, and `calculation_guidance` parameters.

**Root Cause:** `ResearcherState` schema was missing these fields (context_distraction/state.py:19-25)

**Fix:**
- Added three fields to `ResearcherState`:
  ```python
  data_level: Optional[str]
  data_source: Optional[str]
  calculation_guidance: Optional[str]
  ```
- Modified `deep_research` tool to pass all parameters in ainvoke call (context_distraction/tools.py:1407-1409)

**Impact:** Fixed Q4, Q6, Q7 accuracy

---

### 2. **Units Conversion Error**
**Problem:** Researchers converted "$100 million" to 100,000,000 (dollars) instead of 100 (millions), causing NPV to be 107M instead of 108.

**Symptom:**
```python
# Wrong
Initial: 100000000  # dollars
Benefits: [15000000, 18000000, ...]  # dollars
NPV: 107,770,040  # wrong

# Correct
Initial: 100  # millions
Benefits: [15, 18, 21.6, ...]  # millions
NPV: 108.03  # correct
```

**Fix:** Added explicit units guidance to researcher instructions:
```markdown
**CRITICAL: Units Consistency**

When extracting numeric values from research data:
- "$100 million" → extract as **100** (in millions), NOT 100000000 (in dollars)
- "$15M" → extract as **15** (in millions), NOT 15000000 (in dollars)
- Keep ALL calculation values at the same scale throughout
- Return your final answer in the SAME UNITS as the input data
```

**Impact:** Fixed Q4 NPV and Q7 PV calculations

---

### 3. **Calculation Errors**
**Problem:** Researchers manually generated arrays and made arithmetic errors (e.g., year 8: 5377 instead of 53.75, or string "Infinity")

**Fix:** Added systematic calculation approach guidance:
```markdown
**CRITICAL: Systematic Calculation Approach**

For multi-step calculations, follow this process:
1. **Identify what you need** - List all intermediate values required
2. **Calculate each using tools** - Use calculation tools, not mental arithmetic
3. **Use exact tool results** - When a tool returns a value, use that EXACT value in your next step
4. **Verify consistency** - Check that all parameters come from your calculated results
```

**Impact:** Improved calculation reliability across all questions

---

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

### Remaining Issues (Q8, Q9)
- Q8: Market share percentage (24.99 vs 41.69) - Calculation or data source issue
- Q9: Weighted average NPV (868.84 vs 96.01) - Likely units or parameter issue

### Potential Improvements
1. Add validation to calculation tools (reject obviously wrong inputs)
2. Better error messages when tools fail
3. Researcher should verify its answer before storing
4. Supervisor could validate deliverable values (sanity checks)

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
