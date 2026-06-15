Fix v4: Linear bias thua Normalize (Event là Attractor).

Định luật mới:

NON-LINEAR COOPERATIVITY: Sensitivity = (1 + State * k)^2.Nếu State cao, "thụ thể" nhận tín hiệu phình to theo bình phương.(Giống cơ chế cooperative binding trong sinh học).

BISTABILITY: Cùng một Event, qua hai lăng kính khác nhau,sẽ bị bẻ cong thành hai thực thể hoàn toàn đối lập.

Giảm Dissipation để Positive Feedback Loop có cơ hội tích lũy thành Baseline."""

import random

class SimConcept:def init(self, name, baseline, opposes=None):self.name = nameself.baseline = baselineself.activation = baselineself.opposes = opposes or []

def __repr__(self):
    return f"{self.name:12}: B={self.baseline:.3f} | A={self.activation:.3f}"

class SimulationGraph:def init(self, seed_state: dict):opposites_map = {"Self_Doubt": ["Growth", "Self_Worth"],"Growth": ["Self_Doubt", "Cynicism"],"Cynicism": ["Trust", "Growth"],"Trust": ["Cynicism"],"Self_Worth": ["Self_Doubt"]}self.concepts = {name: SimConcept(name, bl, opposites_map.get(name, [])) for name, bl in seed_state.items()}

def get_dominant(self) -> SimConcept:
    return max(self.concepts.values(), key=lambda c: c.baseline)

def get_state_vector(self) -> dict:
    return {c.name: c.activation for c in self.concepts.values()}

def _clamp_and_normalize(self):
    for c in self.concepts.values():
        c.activation = max(0.0, c.activation)
    total = sum(c.activation for c in self.concepts.values())
    if total == 0:
        uniform = 1.0 / len(self.concepts)
        for c in self.concepts.values(): c.activation = uniform
    else:
        for c in self.concepts.values(): c.activation /= total

def spike_from_cooperative_profile(self, base_profile: dict, state_vector: dict, cooperativity_k: float = 2.0):
    """
    ĐỊNH LUẬT CỘNG HƯỞNG PHI TUYẾN:
    Sensitivity = (1 + State * k)^2
    Nếu đang Growth (0.6), sensitivity = (1 + 1.2)^2 = 4.84x.
    Nếu đang Self_Doubt (0.2), sensitivity = (1 + 0.4)^2 = 1.96x.
    => Cùng 1 đơn vị Event, Growth nhận gấp 2.5 lần so với Self_Doubt.
    """
    biased_profile = {}
    
    for concept, base_weight in base_profile.items():
        if concept not in self.concepts: continue
        current_state = state_vector.get(concept, 0.0)
        
        # Công thức cooperativity
        sensitivity = (1.0 + (current_state * cooperativity_k)) ** 2
        biased_weight = base_weight * sensitivity
        biased_profile[concept] = biased_weight
        
    # Normalize để giữ Simplex
    profile_total = sum(biased_profile.values())
    if profile_total > 0:
        for concept in biased_profile:
            biased_profile[concept] /= profile_total
            
    for concept, weight in biased_profile.items():
        self.concepts[concept].activation += weight
        
    self._clamp_and_normalize()

def decay_and_learn(self):
    # Tăng alpha lên một chút để Baseline học nhanh hơn từ thay đổi phi tuyến
    alpha = 0.008 
    for c in self.concepts.values():
        c.baseline = (c.baseline * (1 - alpha)) + (c.activation * alpha)
        c.baseline = max(0.0, min(1.0, c.baseline))
        
    for c in self.concepts.values():
        c.activation += (c.baseline - c.activation) * 0.1
        
    # GIẢM Dissipation: Đừng giết positive feedback quá nhanh
    avg = 1.0 / len(self.concepts)
    for c in self.concepts.values():
        excess = c.activation - avg
        if excess > 0:
            tax = excess * 0.02 # Giảm từ 0.05 xuống 0.02
            c.activation -= tax
            
    self._clamp_and_normalize()

BASE_EVENT_PROFILES = {"Sếp khen thành tích": {"Growth": 0.5, "Trust": 0.3, "Self_Worth": 0.2},"Sếp chửi vì bug":    {"Self_Doubt": 0.4, "Cynicism": 0.3, "Growth": 0.2, "Trust": 0.1},"User nói cảm ơn":    {"Trust": 0.5, "Growth": 0.3, "Self_Worth": 0.2},"User phàn nàn":      {"Self_Doubt": 0.4, "Cynicism": 0.4, "Growth": 0.2},"Code chạy ngon":     {"Growth": 0.5, "Self_Worth": 0.3, "Trust": 0.2},"Server sập":         {"Self_Doubt": 0.5, "Cynicism": 0.4, "Growth": 0.1},"Được tăng lương":    {"Growth": 0.4, "Trust": 0.4, "Self_Worth": 0.2},"Bị cắt thưởng":      {"Cynicism": 0.5, "Self_Doubt": 0.3, "Growth": 0.2},"Đọc được bài hay":   {"Growth": 0.6, "Trust": 0.2, "Self_Worth": 0.2},"Ốm phải nghỉ làm":  {"Self_Doubt": 0.4, "Self_Worth": 0.4, "Growth": 0.2},"Hoàn thành dự án":  {"Growth": 0.6, "Self_Worth": 0.2, "Trust": 0.2},"Gặp khó khăn":      {"Self_Doubt": 0.3, "Growth": 0.4, "Cynicism": 0.3}}

def run_attractor_test(seed: dict, runs: int = 10000, seed_id: int = 0):print(f"\n{'='*70}")print(f"SIMULATION {seed_id}")print(f"{'='*70}")

graph = SimulationGraph(seed)
graph._clamp_and_normalize()

event_pool = list(BASE_EVENT_PROFILES.keys())
checkpoints = [0, 100, 1000, 5000, 10000]

for i in range(1, runs + 1):
    event = random.choice(event_pool)
    base_profile = BASE_EVENT_PROFILES[event]
    current_state = graph.get_state_vector()
    
    graph.spike_from_cooperative_profile(base_profile, current_state, cooperativity_k=2.0)
    graph.decay_and_learn()
    
    if i in checkpoints:
        print(f"\n[Step {i:05d}] Dominant: {graph.get_dominant().name}")
        for c in graph.concepts.values():
            print(f"  {c}")

return graph

def main():SEED_A = {"Growth": 0.35, "Self_Doubt": 0.25, "Cynicism": 0.10, "Trust": 0.15, "Self_Worth": 0.15}SEED_B = {"Growth": 0.25, "Self_Doubt": 0.35, "Cynicism": 0.10, "Trust": 0.15, "Self_Worth": 0.15}

print("=" * 70)
print("ATTRACTOR TEST v5: NON-LINEAR COOPERATIVITY (Confirmation Bias)")
print("Công thức: Weight = Base_Weight * (1 + State * 2)^2")
print("Nếu đang Growth: Nhận tín hiệu gấp 4 lần.")
print("Nếu đang Self_Doubt: Nhận tín hiệu gấp 1.9 lần.")
print("=> Mạnh thắng mạnh. Yếu ngày càng yếu.")
print("=" * 70)

random.seed(42)
result_a = run_attractor_test(SEED_A, seed_id="A (Growth 0.35)")
final_a = {c.name: round(c.baseline, 3) for c in result_a.concepts.values()}

random.seed(42)
result_b = run_attractor_test(SEED_B, seed_id="B (Self_Doubt 0.35)")
final_b = {c.name: round(c.baseline, 3) for c in result_b.concepts.values()}

print("\n" + "=" * 70)
print("FINAL ATTRACTOR STATES (STEP 10,000)")
print("=" * 70)
print(f"{'Concept':<12} | {'Bot A':<8} | {'Bot B':<8}")
print("-" * 35)
for name in final_a.keys():
    print(f"{name:<12} | {final_a[name]:<8} | {final_b[name]:<8}")

dom_a = max(final_a, key=final_a.get)
dom_b = max(final_b, key=final_b.get)

print("\n" + "=" * 70)
if dom_a == dom_b and abs(final_a[dom_a] - final_b[dom_b]) < 0.05:
    print("[STALE] Hệ vẫn ergodic. Environment thắng.")
elif dom_a != dom_b:
    print("[PROVEN] BISTABLE LOCAL ATTRACTORS.")
    print(f"Bot A -> {dom_a}-dominant ({final_a[dom_a]})")
    print(f"Bot B -> {dom_b}-dominant ({final_b[dom_b]})")
    print("=> State bẻ cong Event đủ mạnh để tạo ra hai thực thể khác biệt.")
else:
    print("[WEAK] Cùng dominant, khác cường độ.")
print("=" * 70)

