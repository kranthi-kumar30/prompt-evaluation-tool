import streamlit as st
from runner.test_runner import run_prompt_evaluation

st.set_page_config(page_title="Prompt Evaluator", layout="wide")

st.title("Prompt Evaluator Tool")
st.caption("5-pillar **prompt-only** evaluation — designed for prompt engineering training")

FRAMEWORK_INTRO = """
**Prompt Quality Framework** — five questions every prompt should answer:

| Pillar | Question |
|--------|----------|
| **Clarity** | Can the AI understand what you want? |
| **Specificity** | How detailed is your request? |
| **Context completeness** | Did you provide enough background? |
| **Constraint quality** | Did you tell the AI how to respond? |
| **Ambiguity & risk** | Can the AI misunderstand your request? |
"""

prompt = st.text_area("Enter Prompt", height=220, value="Explain testing.")

question = st.text_input("Enter Question (optional)", value="")

preview_llm = st.checkbox("Preview LLM response (optional — not scored)", value=False)

if st.button("Evaluate Prompt", type="primary"):
    if not prompt.strip():
        st.error("Please enter a prompt.")
        st.stop()

    with st.spinner("Analyzing prompt..."):
        result, llm_preview = run_prompt_evaluation(prompt, question, preview_llm=preview_llm)

    st.subheader(f"Prompt Quality Score: {result.final_score()} / 100")

    with st.expander("Prompt Quality Framework (what we measure)", expanded=False):
        st.markdown(FRAMEWORK_INTRO)

    cols = st.columns(5)
    for i, (pillar_name, pillar_score, pillar_question, _) in enumerate(result.pillars_for_ui()):
        with cols[i]:
            st.metric(pillar_name, f"{pillar_score:.2f}")
            st.caption(pillar_question)

    if result.strengths:
        st.subheader("Strengths Detected")
        for s in result.strengths:
            st.markdown(f"- ✅ {s}")

    st.subheader("Pillar Breakdown")
    for pillar_name, pillar_score, pillar_question, metrics in result.pillars_for_ui():
        with st.expander(f"{pillar_name} — {pillar_score:.2f}", expanded=pillar_score < 0.75):
            st.caption(pillar_question)
            for label, score, reason in metrics:
                c1, c2 = st.columns([1, 4])
                c1.write(f"**{label}**")
                c1.write(f"{score:.2f}")
                c2.caption(reason or "—")

    st.subheader("Weaknesses & Suggestions")
    if result.weakness_items:
        for weakness, suggestion in result.weakness_items:
            st.markdown(f"❌ **{weakness}**")
            st.markdown(f'**Suggestion:** Add: "{suggestion}"')
            st.markdown("")
    else:
        st.success("No weaknesses detected — prompt meets industry quality standards.")

    if result.optional_tips:
        with st.expander("Optional enhancements (not required for a high score)"):
            st.caption("These are nice-to-have improvements only. Your score is not reduced for omitting them.")
            for tip_title, tip_detail in result.optional_tips:
                st.markdown(f"💡 **{tip_title}**")
                st.caption(tip_detail)

    st.subheader("Suggested Enhanced Prompt")
    if result.suggested_prompt.strip() == prompt.strip():
        st.success("Your prompt is already excellent — no changes suggested.")
    else:
        st.caption(
            "Weak prompts receive a full professional rewrite. "
            "Strong prompts (75–94) keep your original and append only missing items."
        )
        st.code(result.suggested_prompt, language=None)

    if llm_preview:
        st.subheader("LLM Preview (informational)")
        st.write(llm_preview)
