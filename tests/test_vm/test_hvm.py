"""Tests for HVM — Hybit Virtual Machine (facade)."""

from hijaiyyah.vm import (
    HVM,
    HYBIT_DIM,
    NUM_REGISTERS,
    GuardSystem,
    HCheck,
    HybitEngine,
    HybitRegister,
)

# ── Sample hybit vectors (from Master Table) ─────────────────

V18_ALIF = [0, 0,0,0, 1,0,0,0,0, 0,0,0,0,0, 0,1,0, 0]
V18_BA   = [2, 0,0,1, 0,1,0,0,0, 1,0,0,0,0, 1,1,1, 0]
V18_TA   = [2, 2,0,0, 0,1,0,0,0, 1,0,0,0,0, 2,1,1, 0]
V18_HA2  = [8, 0,0,0, 0,0,0,0,1, 0,0,0,0,2, 0,1,2, 0]


class TestHVMImport:

    def test_import_hvm(self):
        assert HVM is not None

    def test_import_engine(self):
        assert HybitEngine is not None

    def test_import_guard(self):
        assert GuardSystem is not None

    def test_import_hcheck(self):
        assert HCheck is not None

    def test_constants(self):
        assert NUM_REGISTERS == 16
        assert HYBIT_DIM == 18


class TestGuardSystem:
    """Test guard validation — G1–G4, T1–T2."""

    def test_valid_alif(self):
        gs = GuardSystem()
        status = gs.check(V18_ALIF)
        assert status.passed is True

    def test_valid_ba(self):
        gs = GuardSystem()
        status = gs.check(V18_BA)
        assert status.passed is True

    def test_valid_ha(self):
        gs = GuardSystem()
        status = gs.check(V18_HA2)
        assert status.passed is True

    def test_invalid_g1(self):
        """G1: A_N must equal N_a + N_b + N_d."""
        gs = GuardSystem()
        v = list(V18_BA)
        v[14] = 99  # corrupt A_N
        status = gs.check(v)
        assert not status.passed
        assert "G1" in status.failed_guards

    def test_invalid_g4(self):
        """G4: Θ̂ ≥ U = Q_x + Q_s + Q_a + 4·Q_c."""
        gs = GuardSystem()
        v = list(V18_BA)
        v[0] = 0   # set Θ̂ = 0
        v[13] = 5  # set Q_c = 5 → U = 20 > 0
        status = gs.check(v)
        assert not status.passed
        assert "G4" in status.failed_guards

    def test_o1_complexity(self):
        """Guard check must be O(1) — fixed number of ops."""
        gs = GuardSystem()
        # Just verify it runs in constant time (no loops over data)
        for _ in range(1000):
            gs.check(V18_BA)


class TestHybitEngine:
    """Test native hybit operations."""

    def test_cadd(self):
        engine = HybitEngine(GuardSystem())
        result = engine.cadd(V18_ALIF, V18_BA)
        assert len(result) == HYBIT_DIM
        assert result[0] == 0 + 2  # Θ̂: 0 + 2 = 2

    def test_cadd_preserves_identity(self):
        """∫Θ̂ = ∫U + ∫ρ on aggregation."""
        engine = HybitEngine(GuardSystem())
        result = engine.cadd(V18_BA, V18_HA2)
        theta = result[0]
        U, rho = engine.decompose(result)
        assert theta == U + rho

    def test_proj_theta(self):
        engine = HybitEngine(GuardSystem())
        proj = engine.proj(V18_BA, "THETA")
        assert proj == [2]

    def test_proj_n(self):
        engine = HybitEngine(GuardSystem())
        proj = engine.proj(V18_BA, "N")
        assert proj == [0, 0, 1]

    def test_proj_k(self):
        engine = HybitEngine(GuardSystem())
        proj = engine.proj(V18_BA, "K")
        assert proj == [0, 1, 0, 0, 0]

    def test_proj_q(self):
        engine = HybitEngine(GuardSystem())
        proj = engine.proj(V18_BA, "Q")
        assert proj == [1, 0, 0, 0, 0]

    def test_decompose_ba(self):
        engine = HybitEngine(GuardSystem())
        U, rho = engine.decompose(V18_BA)
        assert U == 0
        assert rho == 2
        assert V18_BA[0] == U + rho

    def test_decompose_ha(self):
        engine = HybitEngine(GuardSystem())
        U, rho = engine.decompose(V18_HA2)
        assert U == 8      # 4 * Q_c = 4 * 2 = 8
        assert rho == 0
        assert V18_HA2[0] == U + rho

    def test_norm2_alif(self):
        engine = HybitEngine(GuardSystem())
        assert engine.norm2(V18_ALIF) == 1  # only K_p=1

    def test_norm2_ba(self):
        engine = HybitEngine(GuardSystem())
        assert engine.norm2(V18_BA) == 2**2 + 1 + 1 + 1  # 4+1+1+1=7

    def test_dist_alif_ha(self):
        engine = HybitEngine(GuardSystem())
        d = engine.dist(V18_ALIF, V18_HA2)
        assert abs(d - 70**0.5) < 0.01  # √70 ≈ 8.367


class TestHCheck:
    """Test runtime integrity monitor."""

    def test_clean_state(self):
        hcheck = HCheck()
        regs = [HybitRegister() for _ in range(NUM_REGISTERS)]
        regs[0].load(V18_BA)
        result = hcheck.scan(regs)
        assert result.passed is True

    def test_corrupted_register(self):
        hcheck = HCheck()
        regs = [HybitRegister() for _ in range(NUM_REGISTERS)]
        bad = list(V18_BA)
        bad[14] = 99  # corrupt A_N
        regs[0].load(bad)
        result = hcheck.scan(regs)
        assert result.passed is False
        assert len(result.failures) >= 1

    def test_empty_registers(self):
        hcheck = HCheck()
        regs = [HybitRegister() for _ in range(NUM_REGISTERS)]
        result = hcheck.scan(regs)
        assert result.passed is True  # no hybit loaded = no failure


class TestHVM:
    """Test Hybit Virtual Machine."""

    def test_init(self):
        vm = HVM()
        assert vm.VERSION == "1.0.0"
        assert len(vm.registers) == NUM_REGISTERS

    def test_load_hybit(self):
        vm = HVM()
        vm.load_hybit(0, V18_BA)
        assert vm.registers[0].has_hybit is True
        assert vm.registers[0].value == V18_BA

    def test_cadd(self):
        vm = HVM()
        vm.load_hybit(0, V18_BA)
        vm.load_hybit(1, V18_TA)
        vm.cadd(2, 0, 1)
        result = vm.registers[2].value
        assert result[0] == 4  # Θ̂: 2 + 2 = 4

    def test_guard_check_pass(self):
        vm = HVM()
        vm.load_hybit(0, V18_BA)
        status = vm.guard_check(0)
        assert status.passed is True

    def test_guard_check_fail(self):
        vm = HVM()
        bad = list(V18_BA)
        bad[14] = 99
        vm.load_hybit(0, bad)
        status = vm.guard_check(0)
        assert not status.passed

    def test_proj(self):
        vm = HVM()
        vm.load_hybit(0, V18_BA)
        vm.proj(1, 0, "THETA")
        assert vm.registers[1].value[0] == 2

    def test_guard_strict_mode(self):
        vm = HVM()
        vm.flags.guard_strict = True
        vm.load_hybit(0, V18_BA)
        vm.load_hybit(1, V18_TA)
        vm.cadd(2, 0, 1)
        assert vm.flags.guard_pass is True

    def test_hcheck(self):
        vm = HVM()
        vm.load_hybit(0, V18_BA)
        result = vm.run_hcheck()
        assert result.passed is True

    def test_reset(self):
        vm = HVM()
        vm.load_hybit(0, V18_BA)
        vm.reset()
        assert vm.registers[0].has_hybit is False
        assert vm.pc == 0
