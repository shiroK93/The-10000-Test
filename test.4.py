"""
BOT 7.36 — Attractor Test v4 (The True Feedback Loop)
========================================================
Fix v3: Markov Mixer (Mất Path Dependence)

Định luật mới:
1. EVENT PROFILE BỊ BẺ CONG BỞI STATE (Path Dependence).
   Cùng "Sếp chửi", qua lăng kính Growth -> spike Growth.
   Qua lăng kính Self_Doubt -> spike Self_Doubt.
2. Profile sau khi bẻ cong PHẢI SUM = 1.0 (Không vi phạm Simplex).
3. Giữ nguyên v3 Physics (Clamp, Normalize, Dissipation).
"""

import random

class SimConcept:
    def __init__(self, name, baseline, opposes=None):
        self.name = name
        self.baseline = baseline
        self.activation = baseline
        self.opposes = opposes or []
        
    def __repr__(self):
        return f"{self.name:12}: B={self.baseline:.3f} | A={self.activation:.3f}"

class SimulationGraph:
    def __init__(self, seed_state: dict):
        opposites_map = {
            "Self_Doubt": ["Growth", "Self_Worth"],
            "Growth": ["Self_Doubt", "Cynicism"],
            "Cynicism": ["Trust", "Growth"],
            "Trust": ["Cynicism"],
            "Self_Worth": ["Self_Doubt"]
        }
        self.concepts = {name: SimConcept(name, bl, opposites_map.get(name, [])) for name, bl in seed_state.items()}

    def get_dominant(self) -> SimConcept:
        return max(self.concepts.values(), key=lambda c: c.baseline)

    def get_state_vector(self) -> dict:
        """Export current activation làm lăng kính"""
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

    def spike_from_biased_profile(self, base_profile: dict, state_vector: dict, bias_strength: float = 0.6):
        """
        ĐỊNH LUẬT VA CHẠM: Profile bị bẻ cong bởi State (Lens Effect).
        bias_strength: Mạnh bao nhiêu (0.0 = Markov, 1.0 = Hoàn toàn bị state chi phối)
        """
        biased_profile = {}
        
        for concept, base_weight in base_profile.items():
            if concept not in self.concepts: continue
            
            # Lấy trọng lượng hiện tại của concept này
            current_state = state_vector.get(concept, 0.0)
            
            # BẺ CONG: Càng mạnh trong state -> Event càng kích thích nó mạnh hơn
            # Đây chính là "Quan điểm làm bẻ cong thực tại"
            biased_weight = base_weight + (current_state * bias_strength)
            biased_profile[concept] = biased_weight
            
        # Normalize profile để tổng = 1.0 (Giữ Pure Simplex khi ném vào Graph)
        profile_total = sum(biased_profile.values())
        if profile_total > 0:
            for concept in biased_profile:
                biased_profile[concept] /= profile_total
                
        # Apply vào Graph
        for concept, weight in biased_profile.items():
            self.concepts[concept].activation += weight
            
        self._clamp_and_normalize()

    def decay_and_learn(self):
        alpha = 0.005
        for c in self.concepts.values():
            c.baseline = (c.baseline * (1 - alpha)) + (c.activation * alpha)
            c.baseline = max(0.0, min(1.0, c.baseline))
            
        for c in self.concepts.values():
            c.activation += (c.baseline - c.activation) * 0.1
            
        avg = 1.0 / len(self.concepts)
        for c in self.concepts.values():
            excess = c.activation - avg
            if excess > 0:
                tax = excess * 0.05
                c.activation -= tax
                
        self._clamp_and_normalize()


# ━━━ BASE EVENT PROFILES (Chỉ là "vật chất thô", chưa qua lăng kính) ━━━
BASE_EVENT_PROFILES = {
    "Sếp khen thành tích": {"Growth": 0.5, "Trust": 0.3, "Self_Worth": 0.2},
    "Sếp chửi vì bug":    {"Self_Doubt": 0.4, "Cynicism": 0.3, "Growth": 0.2, "Trust": 0.1},
    "User nói cảm ơn":    {"Trust": 0.5, "Growth": 0.3, "Self_Worth": 0.2},
    "User phàn nàn":      {"Self_Doubt": 0.4, "Cynicism": 0.4, "Growth": 0.2},
    "Code chạy ngon":     {"Growth": 0.5, "Self_Worth": 0.3, "Trust": 0.2},
    "Server sập":         {"Self_Doubt": 0.5, "Cynicism": 0.4, "Growth": 0.1},
    "Được tăng lương":    {"Growth": 0.4, "Trust": 0.4, "Self_Worth": 0.2},
    "Bị cắt thưởng":      {"Cynicism": 0.5, "Self_Doubt": 0.3, "Growth": 0.2},
    "Đọc được bài hay":   {"Growth": 0.6, "Trust": 0.2, "Self_Worth": 0.2},
    "Ốm phải nghỉ làm":  {"Self_Doubt": 0.4, "Self_Worth": 0.4, "Growth": 0.2},
    "Hoàn thành dự án":  {"Growth": 0.6, "Self_Worth": 0.2, "Trust": 0.2},
    "Gặp khó khăn":      {"Self_Doubt": 0.3, "Growth": 0.4, "Cynicism": 0.3}
}


def run_attractor_test(seed: dict, runs: int = 10000, seed_id: int = 0):
    print(f"\n{'='*70}")
    print(f"SIMULATION {seed_id}")
    print(f"{'='*70}")
    
    graph = SimulationGraph(seed)
    graph._clamp_and_normalize()
    
    event_pool = list(BASE_EVENT_PROFILES.keys())
    checkpoints = [0, 100, 1000, 5000, 10000]
    
    for i in range(1, runs + 1):
        event = random.choice(event_pool)
        
        # 1. Lấy vật chất thô (Base Profile)
        base_profile = BASE_EVENT_PROFILES[event]
        
        # 2. Lấy lăng kính hiện tại (State Vector)
        current_state = graph.get_state_vector()
        
        # 3. VA CHẠM: Ném vật chất qua lăng kính -> Profile bị bẻ cong
        graph.spike_from_biased_profile(base_profile, current_state, bias_strength=0.6)
        
        # 4. Thời gian trôi qua (Decay, Learn, Dissipate)
        graph.decay_and_learn()
        
        if i in checkpoints:
            print(f"\n[Step {i:05d}] Dominant: {graph.get_dominant().name}")
            for c in graph.concepts.values():
                print(f"  {c}")
            total_a = sum(c.activation for c in graph.concepts.values())
            total_b = sum(c.baseline for c in graph.concepts.values())
            print(f"  [PHYSICS] Act Sum: {total_a:.4f} | Base Sum: {total_b:.4f}")

    return graph

def main():
    SEED_A = {"Growth": 0.35, "Self_Doubt": 0.25, "Cynicism": 0.10, "Trust": 0.15, "Self_Worth": 0.15}
    SEED_B = {"Growth": 0.25, "Self_Doubt": 0.35, "Cynicism": 0.10, "Trust": 0.15, "Self_Worth": 0.15}

    print("=" * 70)
    print("ATTRACTOR TEST v4: TRUE FEEDBACK LOOP")
    print("1. Simplex Physics (v3): Không âm, Sum = 1.")
    print("2. Path Dependence (v2): Cùng Event -> Khác Profile nếu Khác State.")
    print("3. Event là 'vật chất'. State là 'lăng kính'. Kết quả là 'vết biến dạng'.")
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
        print("[STALE] Initial difference bị nuốt chửng.")
    elif dom_a != dom_b:
        print("[PROVEN] DIVERGENT ATTRACTORS VIA PATH DEPENDENCE.")
        print(f"Bot A -> {dom_a}-dominant ({final_a[dom_a]})")
        print(f"Bot B -> {dom_b}-dominant ({final_b[dom_b]})")
        print("=> Cùng vật chất. Khác lăng kính. Khác vết biến dạng.")
    else:
        print("[WEAK] Cùng dominant, khác cường độ.")
    print("=" * 70)

if __name__ == "__main__":
    main()
