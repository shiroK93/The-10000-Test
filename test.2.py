"""
BOT 7.36 — Attractor Test v1 (Conservation of Energy Fix)
=============================================================
Fix: Entropy Collapse (Mọi concept -> 1.0)

Định luật mới: Tổng activation của toàn bộ hệ = 1.0
Khi một concept spike, nó PHẢI đánh cắp năng lượng từ concept đối lập.
Không có gì được tạo ra từ hư vô.
"""

import random
import math

class SimConcept:
    def __init__(self, name, baseline, opposes=None):
        self.name = name
        self.baseline = baseline
        self.activation = baseline
        self.opposes = opposes or []
        self.reinforcement_count = 0
        
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
        
        self.concepts = {}
        for name, bl in seed_state.items():
            self.concepts[name] = SimConcept(name, bl, opposites_map.get(name, []))
            
        self.step = 0

    def get_dominant(self) -> SimConcept:
        return max(self.concepts.values(), key=lambda c: c.baseline)

    def _normalize(self):
        """ĐỊNH LUẬT BẢO TỒN NĂNG LƯỢNG: Tổng activation luôn = 1.0"""
        total = sum(c.activation for c in self.concepts.values())
        if total == 0: return # Tránh chia 0
        for c in self.concepts.values():
            c.activation /= total

    def spike(self, concept_name: str, amount: float):
        if concept_name not in self.concepts: return
        c = self.concepts[concept_name]
        
        # 1. Tăng năng lượng cho target
        c.activation += amount
        c.reinforcement_count += 1
        
        # 2. ĐÁNH CẮP NĂNG LƯỢNG từ đối lập (Zero-sum)
        stolen_per_opp = (amount * 0.6) / len(c.opposes) if c.opposes else 0
        for opp_name in c.opposes:
            if opp_name in self.concepts:
                self.concepts[opp_name].activation -= stolen_per_opp
                
        # 3. Normalize để fix lượng năng lượng rò rỉ
        self._normalize()

    def decay_and_learn(self):
        for c in self.concepts.values():
            # 1. Activation kéo về baseline (Relaxation)
            c.activation += (c.baseline - c.activation) * 0.1
            
            # 2. Baseline học hỏi (Exponential Moving Average)
            # Lưu ý: Không cộng dồn trực tiếp nữa. Dùng EMA để tránh phình to.
            learning_rate = 0.002
            c.baseline = (c.baseline * (1 - learning_rate)) + (c.activation * learning_rate)
            
        # Normalize lại sau khi chuyển hóa năng lượng
        self._normalize()


def interpret_event(event: str, graph: SimulationGraph) -> str:
    sorted_concepts = sorted(graph.concepts.values(), key=lambda c: c.activation, reverse=True)
    top1 = sorted_concepts[0].name
    
    if top1 in ["Self_Doubt", "Cynicism"]:
        if "khen" in event or "tốt" in event: return "Cynicism"
        return "Self_Doubt"
    elif top1 in ["Growth", "Trust"]:
        if "chửi" in event or "lỗi" in event: return "Growth"
        return "Growth"
    elif top1 == "Self_Worth": return "Self_Worth"
    return top1


def run_attractor_test(seed: dict, runs: int = 10000, seed_id: int = 0):
    print(f"\n{'='*70}")
    print(f"STARTING SIMULATION {seed_id} | EVENTS: {runs}")
    print(f"{'='*70}")
    
    # Khởi tạo activation sao cho tổng = 1.0 ngay từ đầu
    graph = SimulationGraph(seed)
    graph._normalize() 
    
    event_pool = [
        "Sếp khen thành tích", "Sếp chửi vì bug", "User nói cảm ơn", "User phàn nàn",
        "Code chạy ngon", "Server sập", "Được tăng lương", "Bị cắt thưởng",
        "Đọc được bài hay", "Ốm phải nghỉ làm", "Hoàn thành dự án", "Gặp khó khăn"
    ]
    
    checkpoints = [0, 100, 500, 2000, 5000, 10000]
    
    for i in range(1, runs + 1):
        event = random.choice(event_pool)
        triggered = interpret_event(event, graph)
        
        # Spike lượng nhỏ để thấy cạnh tranh từ từ, không bị bùng nổ
        graph.spike(triggered, 0.15)
        graph.decay_and_learn()
        
        if i in checkpoints:
            print(f"\n[Step {i:05d}] Dominant: {graph.get_dominant().name}")
            for c in graph.concepts.values():
                print(f"  {c}")
            # Verify physics
            total = sum(c.activation for c in graph.concepts.values())
            print(f"  [PHYSICS CHECK] Total Energy: {total:.4f} (Must be 1.0)")

    return graph

def main():
    # Seed bắt đầu với phân bố khác nhau
    SEED_A = {"Growth": 0.35, "Self_Doubt": 0.25, "Cynicism": 0.10, "Trust": 0.15, "Self_Worth": 0.15}
    SEED_B = {"Growth": 0.25, "Self_Doubt": 0.35, "Cynicism": 0.10, "Trust": 0.15, "Self_Worth": 0.15}

    print("=" * 70)
    print("ATTRACTOR TEST v1: CONSERVATION OF ENERGY")
    print("Tổng năng lượng hệ thống LUÔN = 1.0.")
    print("Nếu Growth ăn, Self_Doubt phải đói.")
    print("=" * 70)

    random.seed(42)
    result_a = run_attractor_test(SEED_A, seed_id="A (Growth 0.35)")
    final_a = {c.name: round(c.baseline, 3) for c in result_a.concepts.values()}

    random.seed(42)
    result_b = run_attractor_test(SEED_B, seed_id="B (Self_Doubt 0.35)")
    final_b = {c.name: round(c.baseline, 3) for c in result_b.concepts.values()}

    print("\n" + "=" * 70)
    print("FINAL BASELINES (THE TRUE ATTRACTOR STATES)")
    print("=" * 70)
    print(f"{'Concept':<12} | {'Bot A':<8} | {'Bot B':<8}")
    print("-" * 35)
    for name in final_a.keys():
        print(f"{name:<12} | {final_a[name]:<8} | {final_b[name]:<8}")

    dom_a = max(final_a, key=final_a.get)
    dom_b = max(final_b, key=final_b.get)
    
    print("\n" + "=" * 70)
    if dom_a == dom_b and final_a == final_b:
        print("[STALE] Hệ thống hội tụ thành một người y hệt nhau (Vẫn còn yếu).")
    elif dom_a == dom_b:
        print("[CONVERGENT ATTRACTOR] Cùng dominant, nhưng profile cảm xúc khác nhau.")
    else:
        print("[DIVERGENT] Initial personality thắng Homeostasis.")
        print(f"Bot A trở thành: {dom_a}-oriented.")
        print(f"Bot B trở thành: {dom_b}-oriented.")
        print("=> PERSONALITY ĐƯỢC BẢO TỒN QUA 10,000 EVENTS.")
    print("=" * 70)

if __name__ == "__main__":
    main()
