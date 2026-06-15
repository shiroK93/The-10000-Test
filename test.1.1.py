"""
BOT 7.36 — Attractor Test v2 (True Zero-Sum Dynamics)
Restored version from flattened research source.
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
            "Self_Worth": ["Self_Doubt"],
        }

        self.concepts = {}
        for name, bl in seed_state.items():
            self.concepts[name] = SimConcept(
                name,
                bl,
                opposites_map.get(name, [])
            )

    def get_dominant(self):
        return max(self.concepts.values(), key=lambda c: c.baseline)

    def _normalize(self):
        total = sum(c.activation for c in self.concepts.values())
        if total == 0:
            return

        for c in self.concepts.values():
            c.activation /= total

    def spike(self, concept_name: str, amount: float):
        if concept_name not in self.concepts:
            return

        c = self.concepts[concept_name]
        c.activation += amount

        if c.opposes:
            stolen_per_opp = amount / len(c.opposes)

            for opp_name in c.opposes:
                if opp_name in self.concepts:
                    self.concepts[opp_name].activation -= stolen_per_opp

        self._normalize()

    def decay_and_learn(self):
        alpha = 0.005

        for c in self.concepts.values():
            c.baseline = (
                c.baseline * (1 - alpha)
                + c.activation * alpha
            )

        for c in self.concepts.values():
            c.activation += (c.baseline - c.activation) * 0.1

        avg_activation = 1.0 / len(self.concepts)

        for c in self.concepts.values():
            excess = c.activation - avg_activation

            if excess > 0.1 and c.opposes:
                tax = excess * 0.05

                for opp_name in c.opposes:
                    if opp_name in self.concepts:
                        self.concepts[opp_name].activation += (
                            tax / len(c.opposes)
                        )

                c.activation -= tax

        self._normalize()


def interpret_event(event: str, graph: SimulationGraph) -> str:
    sorted_concepts = sorted(
        graph.concepts.values(),
        key=lambda c: c.activation,
        reverse=True,
    )

    top1 = sorted_concepts[0].name

    if top1 in ["Self_Doubt", "Cynicism"]:
        if "khen" in event or "tốt" in event:
            return "Cynicism"
        return "Self_Doubt"

    elif top1 in ["Growth", "Trust"]:
        if "chửi" in event or "lỗi" in event:
            return "Growth"
        return "Growth"

    elif top1 == "Self_Worth":
        return "Self_Worth"

    return top1


def run_attractor_test(seed: dict, runs: int = 10000, seed_id=0):
    print("\\n" + "=" * 70)
    print(f"SIMULATION {seed_id}")
    print("=" * 70)

    graph = SimulationGraph(seed)
    graph._normalize()

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

    checkpoints = [0, 50, 200, 1000, 3000, 7000, 10000]

    for i in range(1, runs + 1):
        event = random.choice(event_pool)

        triggered = interpret_event(event, graph)

        graph.spike(triggered, 0.2)
        graph.decay_and_learn()

        if i in checkpoints:
            print(f"\\n[Step {i:05d}] Dominant: {graph.get_dominant().name}")

            for c in graph.concepts.values():
                print(" ", c)

            total = sum(c.activation for c in graph.concepts.values())
            baseline_sum = sum(c.baseline for c in graph.concepts.values())

            print(
                f" [PHYSICS] Energy: {total:.4f} | "
                f"Baseline Sum: {baseline_sum:.4f}"
            )

    return graph


def main():
    SEED_A = {
        "Growth": 0.35,
        "Self_Doubt": 0.25,
        "Cynicism": 0.10,
        "Trust": 0.15,
        "Self_Worth": 0.15,
    }

    SEED_B = {
        "Growth": 0.25,
        "Self_Doubt": 0.35,
        "Cynicism": 0.10,
        "Trust": 0.15,
        "Self_Worth": 0.15,
    }

    print("=" * 70)
    print("ATTRACTOR TEST v2: ZERO-SUM UNIVERSE")
    print("Nếu Growth ăn, Self_Doubt PHẢI đói.")
    print("Tổng Baseline KHÔNG THỂ vượt 1.0.")
    print("=" * 70)

    random.seed(42)
    result_a = run_attractor_test(SEED_A, seed_id="A (Growth 0.35)")
    final_a = {c.name: round(c.baseline, 3) for c in result_a.concepts.values()}

    random.seed(42)
    result_b = run_attractor_test(SEED_B, seed_id="B (Self_Doubt 0.35)")
    final_b = {c.name: round(c.baseline, 3) for c in result_b.concepts.values()}

    print("\\n" + "=" * 70)
    print("FINAL ATTRACTOR STATES (STEP 10,000)")
    print("=" * 70)

    for name in final_a.keys():
        print(f"{name:<12} | {final_a[name]:<8} | {final_b[name]:<8}")


if __name__ == "__main__":
    main()
