"""Plotting utilities for context confusion demonstrations."""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from IPython.display import display


def plot_final_comparison(production_metrics, minimal_metrics, optimal_metrics, all_tools):
    """
    Plot final comparison between 3 agent configurations.
    
    Creates 2 visualizations:
    1. Bar chart comparing success criteria, LLM trajectory, and tool efficiency
    2. Subplot showing tokens and latency comparison
    
    Also displays a comparison table and prints key findings.
    """
    configs = ["75 Tools (Overload)", "6 Tools (Limited)", "12 Tools Consolidated)"]
    success_scores = [
        production_metrics["success_criteria"],
        minimal_metrics["success_criteria"],
        optimal_metrics["success_criteria"]
    ]
    llm_trajectory_scores = [
        production_metrics["llm_trajectory"],
        minimal_metrics["llm_trajectory"],
        optimal_metrics["llm_trajectory"]
    ]
    efficiency_scores = [
        production_metrics["tool_efficiency"],
        minimal_metrics["tool_efficiency"],
        optimal_metrics["tool_efficiency"]
    ]
    latency_scores = [
        production_metrics["latency"],
        minimal_metrics["latency"],
        optimal_metrics["latency"]
    ]
    token_scores = [
        production_metrics["tokens"],
        minimal_metrics["tokens"],
        optimal_metrics["tokens"]
    ]
    cost_scores = [
        production_metrics["cost"],
        minimal_metrics["cost"],
        optimal_metrics["cost"]
    ]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Success Criteria',
        x=configs,
        y=success_scores,
        marker_color='#22c55e'   # Green
    ))
    fig.add_trace(go.Bar(
        name='LLM Trajectory',
        x=configs,
        y=llm_trajectory_scores,
        marker_color='#a855f7'   # Purple
    ))
    fig.add_trace(go.Bar(
        name='Tool Efficiency',
        x=configs,
        y=efficiency_scores,
        marker_color='#14b8a6'   # Teal
    ))

    fig.update_layout(
        title="Consolidated Tools Deliver Complete, Efficient Responses",
        yaxis_title="Score",
        barmode='group',
        height=450,
        showlegend=True,
        yaxis=dict(range=[0, 1.0]),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    fig.show()

    fig = make_subplots(
        rows=1, cols=2,
        shared_xaxes=False,
        subplot_titles=["Avg Tokens (lower is better)", "Avg Latency (s, lower is better)"],
    )

    fig.add_trace(go.Bar(
        name="Avg Tokens",
        x=configs,
        y=token_scores,
        marker_color="#60a5fa",
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        name="Avg Latency (s)",
        x=configs,
        y=latency_scores,
        marker_color="#fbbf24",
    ), row=1, col=2)

    fig.update_layout(
        title="Consolidated Tools Deliver a Balance of Cheaper, Faster Responses",
        height=450,
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=60, r=40, t=90, b=60),
    )

    fig.update_yaxes(title_text="Tokens", row=1, col=1)
    fig.update_yaxes(title_text="Latency", row=1, col=2)

    fig.show()


    # Create summary table with performance metrics
    comparison_df = pd.DataFrame({
        "Configuration": configs,
        "Tool Count": [len(all_tools), 6, 12],
        "Success Criteria": [f"{s:.1%}" for s in success_scores],
        "LLM Trajectory": [f"{s:.1%}" for s in llm_trajectory_scores],
        "Tool Efficiency": [f"{s:.2f}" for s in efficiency_scores],
        "Avg Latency": [f"{s:.2f}s" for s in latency_scores],
        "Avg Tokens": [f"{s:.0f}" for s in token_scores],
        "Avg Cost": [f"${s:.4f}" for s in cost_scores],
    })

    display(comparison_df)

    print("\n   Key findings: Consolidated tools win across all metrics:")
    print("   • Higher success criteria (complete answers)")
    print("   • Better tool selection (LLM recognizes appropriate patterns)")
    print("   • Improved efficiency (fewer calls, more information)")
    print(f"   • Lower cost: 12-tool agent uses {token_scores[0]/token_scores[2]:.1f}x fewer tokens than 75-tool agent!")


def plot_noise_impact(noise_experiments, get_metrics_from_experiment):
    """
    Plot the impact of irrelevant tools (noise) on agent performance.
    
    Creates a line chart showing how success criteria decreases as the percentage
    of relevant tools decreases.
    
    Also displays a comparison table and prints key findings.
    """
    noise_percentages = [100, 50, 25]
    noise_configs_names = ["100-pct-relevant", "50-pct-relevant", "25-pct-relevant"]

    success_by_noise = []

    for config_name in noise_configs_names:
        metrics = get_metrics_from_experiment(noise_experiments[config_name])
        success_by_noise.append(metrics.get("success_criteria", 0))

    # Visualize the impact
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=noise_percentages,
        y=success_by_noise,
        mode='lines+markers',
        name='Success Criteria',
        line=dict(color='#2ca02c', width=3),
        marker=dict(size=10),
    ))

    fig.update_layout(
        title="Impact of Irrelevant Tools on Agent Performance",
        xaxis_title="% Relevant Tools",
        yaxis_title="Success Criteria Score",
        hovermode='x unified',
        height=400
    )

    fig.show()

    # Create comparison table
    noise_comparison = {
        "% Relevant": noise_percentages,
        "Success Criteria": success_by_noise if success_by_noise[0] > 0 else ["Run eval"] * 3,
    }

    df_noise = pd.DataFrame(noise_comparison)
    display(df_noise)

    print("\nKey Findings:")
    if success_by_noise[0] > 0:
        print(f"   100% relevant tools: {success_by_noise[0]:.2f} success criteria")
        print(f"   25% relevant tools: {success_by_noise[2]:.2f} success criteria")
        degradation = (
            (success_by_noise[0] - success_by_noise[2])
            / success_by_noise[0] * 100
        )
        print(f"   Degradation: {degradation:.0f}% drop in success rate")
    else:
        print("   Run evaluations above to see actual metrics")

    print("   - Even with constant tool count, noise degrades performance")
    print("   - Irrelevant tools lead to incorrect tool calls")
    print("   - Quality of tools matters as much as quantity")


def plot_routing_comparison(worst_noise_metrics, routed_metrics):
    """
    Compare routing solution vs worst noise configuration.
    
    Creates a bar chart comparing LLM trajectory and success criteria scores
    between agents with and without smart routing.
    
    Also displays a comparison table and prints analysis.
    """
    routing_comparison = {
        "Configuration": ["25% Relevant Tools (No Routing)", "Smart Routing"],
        "LLM Trajectory": [worst_noise_metrics.get("llm_trajectory", 0), routed_metrics.get("llm_trajectory", 0)],
        "Success Criteria": [worst_noise_metrics.get("success_criteria", 0), routed_metrics.get("success_criteria", 0)],
        "Tool Efficiency": [worst_noise_metrics.get("tool_efficiency", 0), routed_metrics.get("tool_efficiency", 0)],
    }

    # Create bar chart comparison
    df_routing = pd.DataFrame(routing_comparison)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='25% Relevant (No Routing)',
        x=['LLM Trajectory', 'Success Criteria'],
        y=[worst_noise_metrics.get("llm_trajectory", 0), worst_noise_metrics.get("success_criteria", 0)],
        marker_color='#d62728'
    ))
    fig.add_trace(go.Bar(
        name='Smart Routing',
        x=['LLM Trajectory', 'Success Criteria'],
        y=[routed_metrics.get("llm_trajectory", 0), routed_metrics.get("success_criteria", 0)],
        marker_color='#2ca02c'
    ))

    fig.update_layout(
        title="Routing Solution vs Worst Noise Configuration",
        yaxis_title="Score",
        barmode='group',
        height=400
    )

    fig.show()

    display(df_routing)

    print("\nSmart routing eliminates noise by classifying query intent and providing only relevant tools, maintaining performance through focused context.")


def plot_instruction_bloat(clean_baseline_metrics, bloated_metrics):
    """
    Plot the impact of instruction bloat on agent performance.
    
    Creates a line chart showing how trajectory match, success criteria, and
    tool efficiency degrade when instructions are bloated with irrelevant content.
    
    Also displays a comparison table and prints key findings.
    """
    # Create multi-line plot showing metric degradation
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=['Clean', 'Bloated'],
        y=[clean_baseline_metrics.get("llm_trajectory", 0), bloated_metrics.get("llm_trajectory", 0)],
        mode='lines+markers',
        name='Trajectory',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=10)
    ))

    fig.add_trace(go.Scatter(
        x=['Clean', 'Bloated'],
        y=[clean_baseline_metrics.get("success_criteria", 0), bloated_metrics.get("success_criteria", 0)],
        mode='lines+markers',
        name='Success Criteria',
        line=dict(color='#2ca02c', width=3),
        marker=dict(size=10)
    ))

    fig.add_trace(go.Scatter(
        x=['Clean', 'Bloated'],
        y=[clean_baseline_metrics.get("tool_efficiency", 0), bloated_metrics.get("tool_efficiency", 0)],
        mode='lines+markers',
        name='Tool Efficiency',
        line=dict(color='#ff7f0e', width=3),
        marker=dict(size=10)
    ))

    fig.update_layout(
        title="Impact of Instruction Bloat on Agent Performance",
        yaxis_title="Score",
        yaxis=dict(range=[0, 1.0]),
        height=400,
        hovermode='x unified'
    )

    fig.show()

    # Create comparison table
    instruction_impact = {
        "Metric": ["Trajectory", "Success Criteria", "Tool Efficiency"],
        "Clean Instructions": [
            f"{clean_baseline_metrics.get('llm_trajectory', 0):.2f}",
            f"{clean_baseline_metrics.get('success_criteria', 0):.2f}",
            f"{clean_baseline_metrics.get('tool_efficiency', 0):.2f}"
        ],
        "Bloated Instructions": [
            f"{bloated_metrics.get('llm_trajectory', 0):.2f}",
            f"{bloated_metrics.get('success_criteria', 0):.2f}",
            f"{bloated_metrics.get('tool_efficiency', 0):.2f}"
        ]
    }

    df_instructions = pd.DataFrame(instruction_impact)
    display(df_instructions)

    print("\nKey Findings: Verbose instructions from irrelevant domains degrade trajectory match and success criteria. Focused instructions improve tool selection and agent performance.")
