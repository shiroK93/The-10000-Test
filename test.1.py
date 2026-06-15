"""
BOT 7.36 — The Attractor Test (10,000 Events Simulation)
=======================================================

"Thả cùng một personality vào 10,000 events ngẫu nhiên.
Nó sẽ trở thành ai?"

KHÔNG thêm class.
KHÔNG thêm node.
KHÔNG thêm edge.

Chỉ lấy toán học của 7.36,
ném vào vòng lặp 10,000 lần,
và xem nó trôi về đâu.

Mục tiêu:
Chứng minh First Law of Cognitive Architecture.

> Personality is the attractor state of a feedback system.
"""

import random
import math


# ═══════════════════════════════════════════════════════════════
# LEAN SIMULATION STATE (Pure Math, No I/O overhead)
# ═══════════════════════════════════════════════════════════════

class SimConcept:
    def __init__(self, name, baseline, opposes=None):
        self.name = name
        self.baseline = baseline  # Long-term memory (chậm thay đổi)
        self.activation = baseline  # Short-term working memory (nhanh thay đổi)
        self.opposes = opposes or []  # Le Chatelier's Principle
        self.reinforcement_count = 0

    def __repr__(self):
        return (
            f"{self.name}: "
            f"B={self.baseline:.2f} "
            f"A={self.activation:.2f}"
        )


class SimulationGraph:
    def __init__(self, seed_state: dict):
        """
        seed_state:
            {"Concept_Name": baseline_float, ...}

        opposes được hardcode tạm để test physics.
        """

        opposites_map = {
            "Self_Doubt": ["Growth", "Self_Worth"],
            "Growth": ["Self_Doubt", "Cynicism"],
            "Cynicism": ["Trust", "Growth"],
            "Trust": ["Cynicism"],
            "Self_Worth": ["Self_Doubt"],
        }

        self.concepts = {}

        for name, bl in seed_state.items():
            self.concepts[name] = SimConcept(
                name,
                bl,
                opposites_map.get(name, [])
            )

        self.step = 0
        self.trajectory = []

    def get_dominant(self) -> SimConcept:
        return max(
            self.concepts.values(),
            key=lambda c: c.baseline
        )

    def spike(self, concept_name: str, amount: float):
        if concept_name in self.concepts:
            c = self.concepts[concept_name]
            c.activation = min(1.0, c.activation + amount)
            c.reinforcement_count += 1

    def decay_and_learn(self):
        """
        Mô phỏng giấc ngủ / thời gian trôi qua.

        1. Activation kéo về Baseline (Relaxation).
        2. Baseline dịch chuyển nhẹ về phía Activation.
        3. Homeostatic Pressure (Le Chatelier).
        """

        for c in self.concepts.values():

            # 1. Activation decay về baseline
            diff = c.activation - c.baseline
            c.activation -= diff * 0.2

            # 2. Baseline học hỏi từ activation
            if c.activation > c.baseline:
                c.baseline += (
                    (c.activation - c.baseline) * 0.005
                )
                c.baseline = min(1.0, c.baseline)
            else:
                c.baseline += (
                    (c.activation - c.baseline) * 0.002
                )

        # 3. Homeostasis
        for c in self.concepts.values():
            if c.activation > 0.7:

                pressure = (
                    (c.activation - 0.7) * 0.1
                )

                for opp_name in c.opposes:
                    if opp_name in self.concepts:
                        self.concepts[
                            opp_name
                        ].activation += pressure

    def record_state(self):
        self.trajectory.append(
            {
                c.name: round(c.baseline, 4)
                for c in self.concepts.values()
            }
        )


# ═══════════════════════════════════════════════════════════════
# MOCK DEFORMATION (Feedback Loop Core)
# ═══════════════════════════════════════════════════════════════

def interpret_event(event: str, graph: SimulationGraph) -> str:
    """
    Không dùng LLM.
    Dùng toán học trạng thái.
    Trả về Concept bị kích thích.
    """

    sorted_concepts = sorted(
        graph.concepts.values(),
        key=lambda c: c.activation,
        reverse=True
    )

    top1 = sorted_concepts[0].name
    top2 = (
        sorted_concepts[1].name
        if len(sorted_concepts) > 1
        else "Neutral"
    )

    if top1 in ("Self_Doubt", "Cynicism"):

        # Negativity bias
        if "khen" in event or "tốt" in event:
            return "Cynicism"

        return "Self_Doubt"

    elif top1 in ("Growth", "Trust"):

        # Positivity bias
        if "chửi" in event or "lỗi" in event:
            return "Growth"

        return "Growth"

    elif top1 == "Self_Worth":
        return "Self_Worth"

    return top1


# ═══════════════════════════════════════════════════════════════
# THE SIMULATION ENGINE
# ═══════════════════════════════════════════════════════════════

def run_attractor_test(
    seed: dict,
    runs: int = 10000,
    seed_id: int = 0
):

    print(f"\n{'=' * 70}")
    print(
        f"STARTING SIMULATION {seed_id} | "
        f"SEED: {seed} | EVENTS: {runs}"
    )
    print(f"{'=' * 70}")

    graph = SimulationGraph(seed)

    event_pool = [
        "Sếp khen thành tích",
        "Sếp chửi vì bug",
        "User nói cảm ơn",
        "User phàn nàn",
        "Code chạy ngon",
        "Server sập",
        "Được tăng lương",
        "Bị cắt thưởng",
        "Đọc được bài hay",
        "Ốm phải nghỉ làm",
        "Hoàn thành dự án",
        "Gặp khó khăn",
    ]

    checkpoints = [
        0,
        100,
        500,
        1000,
        2500,
        5000,
        7500,
        10000,
    ]

    for i in range(1, runs + 1):

        # 1. Random Event
        event = random.choice(event_pool)

        # 2. Deformation
        triggered_concept = interpret_event(
            event,
            graph
        )

        # 3. Spike
        graph.spike(triggered_concept, 0.2)

        # 4. Physics
        graph.decay_and_learn()

        # 5. Record
        if i in checkpoints:
            graph.step = i
            graph.record_state()

            dominant = graph.get_dominant()

            print(
                f"\n[Step {i:05d}] "
                f"Dominant: {dominant.name} "
                f"({dominant.baseline:.3f})"
            )

            for c in graph.concepts.values():
                print(f"  {c}")

    return graph


# ═══════════════════════════════════════════════════════════════
# DEMO: CHỨNG MINH ATTRACTOR
# ═══════════════════════════════════════════════════════════════

def main():

    SEED_A = {
        "Growth": 0.55,
        "Self_Doubt": 0.50,
        "Cynicism": 0.30,
        "Trust": 0.40,
        "Self_Worth": 0.45,
    }

    SEED_B = {
        "Growth": 0.50,
        "Self_Doubt": 0.55,
        "Cynicism": 0.30,
        "Trust": 0.40,
        "Self_Worth": 0.45,
    }

    print("=" * 70)
    print("ATTRACTOR PROOF TEST")
    print("Hai tâm trí gần giống hệt (chênh lệch 0.05).")
    print("Nhận CÙNG 10,000 events ngẫu nhiên.")
    print("Câu hỏi: Cuối cùng chúng có trở thành cùng một người không?")
    print("=" * 70)

    # A
    random.seed(42)

    result_a = run_attractor_test(
        SEED_A,
        seed_id="A (Growth slightly higher)"
    )

    final_state_a = result_a.get_dominant().name

    # B
    random.seed(42)

    result_b = run_attractor_test(
        SEED_B,
        seed_id="B (Self_Doubt slightly higher)"
    )

    final_state_b = result_b.get_dominant().name

    print("\n" + "=" * 70)
    print("SIMULATION RESULTS")
    print("=" * 70)

    print(
        f"Bot A Final Personality: {final_state_a}"
    )
    print(
        f"Bot B Final Personality: {final_state_b}"
    )

    if final_state_a == final_state_b:

        print("\n[PROVEN] ATTRACTOR EXISTS.")
        print(
            "Dù bắt đầu với trạng thái khác nhau "
            "(chênh 0.05),"
        )
        print(
            "hệ thống đã tự động hút cả hai "
            f"về cùng một mỏ neo: '{final_state_a}'."
        )
        print(
            "Personality không phải là prompt. "
            "Personality là tính chất vật lý của hệ."
        )

    else:

        print("\n[FAILED] NO STABLE ATTRACTOR.")
        print(
            "Hệ thống nhạy cảm quá mức "
            "với điều kiện ban đầu."
        )
        print(
            "Cần tăng Homeostatic Pressure "
            "hoặc giảm Learning Rate."
        )

    print("=" * 70)


if __name__ == "__main__":
    main()
