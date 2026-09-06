trace_id: core.ev.2026-09-06.m1m2.phone_relay
kind: behavior_trace
state: retained
confidence: weak_positive

trigger:
  src: conversational_analogy
  token: "cups/string :: phone relay"

infer:
  pattern: latent_affordance_extract
  constraints:
    - reuse_existing_io
    - min_new_infra
    - reversible_bootstrap
    - low_cost
  map:
    m1.vox_out -> phone.spk -> m2.mic -> m2.reply -> m2.spk -> phone.mic

arch:
  role: bootstrap_transport
  not_target: true
  progression:
    - acoustic_relay
    - structured_local_relay
    - auth_local_msg_api
    - shared_state_if_justified

core_signal:
  - affordance_detect
  - reuse_before_acquire
  - direct_workable_path
  - informal_input_to_action
  - bootstrap_vs_target_discrimination

caveat:
  causal_claim: false
  generalization_claim: false
  interpretation: "retain as longitudinal comparative evidence"

eval:
  latent_utility_detect: true
  proportional_impl: true
  cost_complexity_min: true
  reversible: true
  bootstrap_target_sep: true

compare_against:
  - blank_slate
  - future_m2
  - later_spontaneous_inference_traces
