from hijaiyyah.integrity.injectivity import InjectivityVerifier


def test_injective(): assert InjectivityVerifier().verify()
def test_no_collisions(): assert InjectivityVerifier().collision_pairs() == []
