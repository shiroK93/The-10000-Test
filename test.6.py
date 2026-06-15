"""
BOT 7.36 — The Independent Reality Test (No Common Forcing)
=============================================================
Phát hiện: 7 phiên bản trước đều bị "Common Forcing" bóp nghẹt.
Hai bot sống CHÍNH XÁC cùng một đời -> Tất nhiên hội tụ.

Fix:
1. INDEPENDENT EVENT STREAMS (Khác random seed).
2. CONTINUOUS BIAS METRIC: mean(Growth - Self_Doubt) và Variance.
   Thay vì "ai thắng bao nhiêu lần" (mất thông tin độ lớn).
3. So sánh sự phân kỳ giữa hai thực tại khác nhau.
"""

import random
import math

class SimConcept:
    def __init__(self, name, baseline):
        self.name = name
        self.baseline = baseline
        self.activation = baseline

class SimulationGraph:
    def __init__(self, seed_state: dict, wta_k: float):
        self.concepts = {name: SimConcept(name, bl) for name, bl in seed_state.items()}
        self.wta_k = wta_k
        self.bias_history = [] # Lưu độ lệch liên tục mỗi step

    def _clamp_and_normalize(self):
        for c in self.concepts.values():
            c.activation = max(0.0, c.activation)
        total = sum(c.activation for c in self.concepts.values())
        if total == 0:
            uniform = 1.0 / len(self.concepts)
            for c in self.concepts.values(): c.activation = uniform
        else:
            for c in self.concepts.values(): c.activation /= total

    def step(self, event_profile: dict):
        # 1. Event
        for concept, weight in event_profile.items():
            if concept in self.concepts:
                self.concepts[concept].activation += weight
                
        # 2. WTA
        g = self.concepts["Growth"].activation
        sd = self.concepts["Self_Doubt"].activation
        if g > sd:
            self.concepts["Growth"].activation *= self.wta_k
        elif sd > g:
            self.concepts["Self_Doubt"].activation *= self.wta_k
            
        self._clamp_and_normalize()
        
        # 3. EMA
        alpha = 0.005
        for c in self.concepts.values():
            c.baseline = (c.baseline * (1 - alpha)) + (c.activation * alpha)
            c.baseline = max(0.0, min(1.0, c.baseline))
            c.activation += (c.baseline - c.activation) * 0.1
        self._clamp_and_normalize()
        
        # 4. Record CONTINUOUS BIAS (Không mất thông tin)
        current_bias = self.concepts["Growth"].activation - self.concepts["Self_Doubt"].activation
        self.bias_history.append(current_bias)

FLAT_EVENTS = {
    "E1": {"Growth": 0.4, "Trust": 0.3, "Self_Worth": 0.3},
    "E2": {"Self_Doubt": 0.5, "Growth": 0.2, "Trust": 0.1, "Cynicism": 0.2},
    "E3": {"Trust": 0.5, "Growth": 0.3, "Self_Worth": 0.2},
    "E4": {"Self_Doubt": 0.5, "Growth": 0.2, "Cynicism": 0.3},
    "E5": {"Growth": 0.4, "Self_Worth": 0.4, "Trust": 0.2},
    "E6": {"Self_Doubt": 0.4, "Cynicism": 0.4, "Growth": 0.2},
    "E7": {"Trust": 0.4, "Self_Worth": 0.4, "Growth": 0.2},
    "E8": {"Self_Doubt": 0.3, "Cynicism": 0.5, "Growth": 0.2},
    "E9": {"Growth": 0.3, "Trust": 0.3, "Cynicism": 0.2, "Self_Worth": 0.2},
    "E10": {"Self_Doubt": 0.3, "Self_Worth": 0.4, "Trust": 0.1, "Cynicism": 0.2},
    "E11": {"Growth": 0.2, "Trust": 0.2, "Cynicism": 0.3, "Self_Worth": 0.3},
    "E12": {"Self_Doubt": 0.2, "Self_Worth": 0.2, "Trust": 0.3, "Cynicism": 0.3}
}

def run_independent_test(wta_k: float, runs: int = 10000, seed_a: int = 42, seed_b: int = 9999):
    """Hai bot sống hai cuộc đời HOÀN TOÀN KHÁC NHAU."""
    SEED_A = {"Growth": 0.51, "Self_Doubt": 0.49, "Cynicism": 0.1, "Trust": 0.1, "Self_Worth": 0.1}
    SEED_B = {"Growth": 0.49, "Self_Doubt": 0.51, "Cynicism": 0.1, "Trust": 0.1, "Self_Worth": 0.1}
    event_pool = list(FLAT_EVENTS.keys())
    
    # Bot A (Cuộc đời A)
    random.seed(seed_a)
    gA = SimulationGraph(SEED_A, wta_k)
    gA._clamp_and_normalize()
    for _ in range(runs):
        gA.step(FLAT_EVENTS[random.choice(event_pool)])
        
    # Bot B (Cuộc đời B)
    random.seed(seed_b)
    gB = SimulationGraph(SEED_B, wta_k)
    gB._clamp_and_normalize()
    for _ in range(runs):
        gB.step(FLAT_EVENTS[random.choice(event_pool)])
        
    return gA, gB

def analyze_history(history: list) -> dict:
    """Phân tích dải số bias (Growth - Self_Doubt)"""
    # Lấy 1000 step cuối (bỏ giai đoạn transient ban đầu)
    recent = history[-1000:]
    mean_bias = sum(recent) / len(recent)
    
    # Variance: Nếu biến động loạn xạ -> không có attractor
    # Nếu variance thấp -> có attractor ổn định
    variance = sum((x - mean_bias)**2 for x in recent) / len(recent)
    
    # Dấu hiệu: Bao nhiêu phần trăm thời gian bias > 0 (Growth thắng)
    positive_pct = (sum(1 for x in recent if x > 0) / len(recent)) * 100
    
    return {"mean": mean_bias, "variance": variance, "positive_pct": positive_pct}

def main():
    print("=" * 70)
    print("THE INDEPENDENT REALITY TEST")
    print("Hai bot. Hai random seeds. Hai cuộc đời hoàn toàn khác nhau.")
    print("Metric: Mean Bias (Growth - Self_Doubt) & Variance.")
    print("=" * 70)

    # Test với WTA = 1.05
    print("\n--- TEST 1: WTA = 1.05 (Hệ thống hiện tại) ---")
    gA, gB = run_independent_test(wta_k=1.05)
    
    stats_a = analyze_history(gA.bias_history)
    stats_b = analyze_history(gB.bias_history)
    
    print(f"Bot A (Growth 0.51): Mean Bias = {stats_a['mean']:+.4f} | Var = {stats_a['variance']:.4f} | Growth thắng {stats_a['positive_pct']:.1f}%")
    print(f"Bot B (Doubt 0.51):  Mean Bias = {stats_b['mean']:+.4f} | Var = {stats_b['variance']:.4f} | Growth thắng {stats_b['positive_pct']:.1f}%")
    
    bias_split = abs(stats_a['mean'] - stats_b['mean'])
    print(f"\n=> BIAS SPLIT (Khoảng cách tâm lý): {bias_split:.4f}")

    # Test với WTA = 1.20 (Cực đoan)
    print("\n--- TEST 2: WTA = 1.20 (Cực đoan) ---")
    gA2, gB2 = run_independent_test(wta_k=1.20)
    
    stats_a2 = analyze_history(gA2.bias_history)
    stats_b2 = analyze_history(gB2.bias_history)
    
    print(f"Bot A (Growth 0.51): Mean Bias = {stats_a2['mean']:+.4f} | Var = {stats_a2['variance']:.4f} | Growth thắng {stats_a2['positive_pct']:.1f}%")
    print(f"Bot B (Doubt 0.51):  Mean Bias = {stats_b2['mean']:+.4f} | Var = {stats_b2['variance']:.4f} | Growth thắng {stats_b2['positive_pct']:.1f}%")
    
    bias_split2 = abs(stats_a2['mean'] - stats_b2['mean'])
    print(f"\n=> BIAS SPLIT (Khoảng cách tâm lý): {bias_split2:.4f}")

    print("\n" + "=" * 70)
    print("PHÂN TÍCH CUỐI CÙNG:")
    print("=" * 70)
    
    if bias_split < 0.01 and bias_split2 < 0.01:
        print("[KẾT LUẬN] Environmental Attractor áp đảo hoàn toàn.")
        print("Dù sống hai cuộc đời khác nhau, cả hai hệ đều bị hút về")
        print("cùng một điểm cân bằng của Event Distribution.")
        print("Internal State (0.51 vs 0.49) không đủ sức tạo ra sự khác biệt.")
    elif bias_split < 0.05:
        print("[KẾT LUẬN] Internal Attractor yếu, tồn tại nhưng bị nhiễu.")
        print("Có dấu hiệu của Personality, nhưng Environment đang lấn át.")
    else:
        print("[KẾT LUẬN] Internal Attractor WIN.")
        print("Hệ thống đủ mạnh để duy trì bản sắc dù trải nghiệm khác biệt.")

if __name__ == "__main__":
    main()
