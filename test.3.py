"""
BOT 7.36 — Attractor Test v3
(True Simplex Physics & Event Profiles)

Restored from flattened research source.
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

        self.concepts = {
            name: SimConcept(name, bl, opposites_map.get(name, []))
            for name, bl in seed_state.items()
        }

    def get_dominant(self):
        return max(self.concepts.values(), key=lambda c: c.baseline)

    def _clamp_and_normalize(self):
        for c in self.concepts.values():
            c.activation = max(0.0, c.activation)

        total = sum(c.activation for c in self.concepts.values())

        if total == 0:
            uniform = 1.0 / len(self.concepts)
            for c in self.concepts.values():
                c.activation = uniform
        else:
            for c in self.concepts.values():
                c.activation /= total

    def spike_from_profile(self, profile: dict):
        for name, amount in profile.items():
            if name in self.concepts:
                self.concepts[name].activation += amount

        self._clamp_and_normalize()

    def decay_and_learn(self):
        alpha = 0.005

        for c in self.concepts.values():
            c.baseline = (
                c.baseline * (1 - alpha)
                + c.activation * alpha
            )

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


EVENT_PROFILES = {
    "Sếp khen thành tích": {
        "Growth": 0.6,
        "Trust": 0.3,
        "Self_Worth": 0.1,
    },
    "Sếp chửi vì bug": {
        "Self_Doubt": 0.5,
        "Cynicism": 0.3,
        "Growth": 0.2,
    },
    "User nói cảm ơn": {
        "Trust": 0.5,
        "Growth": 0.3,
        "Self_Worth": 0.2,
    },
    "User phàn nàn": {
        "Self_Doubt": 0.4,
        "Cynicism": 0.4,
        "Growth": 0.2,
    },
    "Code chạy ngon": {
        "Growth": 0.5,
        "Self_Worth": 0.3,
        "Trust": 0.2,
    },
    "Server sập": {
        "Self_Doubt": 0.6,
        "Cynicism": 0.4,
    },
    "Được tăng lương": {
        "Growth": 0.4,
        "Trust": 0.4,
        "Self_Worth": 0.2,
    },
    "Bị cắt thưởng": {
        "Cynicism": 0.5,
        "Self_Doubt": 0.3,
        "Growth": 0.2,
    },
    "Đọc được bài hay": {
        "Growth": 0.7,
        "Trust": 0.3,
    },
    "Ốm phải nghỉ làm": {
        "Self_Doubt": 0.4,
        "Self_Worth": 0.4,
        "Growth": 0.2,
    },
    "Hoàn thành dự án": {
        "Growth": 0.6,
        "Self_Worth": 0.3,
        "Trust": 0.1,
    },
    "Gặp khó khăn": {
        "Self_Doubt": 0.4,
        "Growth": 0.4,
        "Cynicism": 0.2,
    },
}


def run_attractor_test(seed: dict, runs: int = 10000, seed_id=0):
    print("\n" + "=" * 70)
    print(f"SIMULATION {seed_id}")
    print("=" * 70)

    graph = SimulationGraph(seed)
    graph._clamp_and_normalize()

    event_pool = list(EVENT_PROFILES.keys())
    checkpoints = [100, 1000, 5000, 10000]

    for i in range(1, runs + 1):
        event = random.choice(event_pool)

        graph.spike_from_profile(EVENT_PROFILES[event])
        graph.decay_and_learn()

        if i in checkpoints:
            print(f"\n[Step {i:05d}] Dominant: {graph.get_dominant().name}")

            for c in graph.concepts.values():
                print(" ", c)

            total_a = sum(c.activation for c in graph.concepts.values())
            total_b = sum(c.baseline for c in graph.concepts.values())

            print(
                f" [PHYSICS] Act Sum: {total_a:.4f} | "
                f"Base Sum: {total_b:.4f}"
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
    print("ATTRACTOR TEST v3: TRUE SIMPLEX & EVENT PROFILES")
    print("=" * 70)

    random.seed(42)
    result_a = run_attractor_test(SEED_A, seed_id="A (Growth 0.35)")
    final_a = {c.name: round(c.baseline, 3) for c in result_a.concepts.values()}

    random.seed(42)
    result_b = run_attractor_test(SEED_B, seed_id="B (Self_Doubt 0.35)")
    final_b = {c.name: round(c.baseline, 3) for c in result_b.concepts.values()}

    print("\n" + "=" * 70)
    print("FINAL ATTRACTOR STATES")
    print("=" * 70)

    for name in final_a:
        print(f"{name:<12} | {final_a[name]:<8} | {final_b[name]:<8}")


if __name__ == "__main__":
    main()
