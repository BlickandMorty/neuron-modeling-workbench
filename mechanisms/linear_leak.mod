TITLE Minimal linear leak used to verify the local NMODL toolchain

NEURON {
    SUFFIX linearleak
    NONSPECIFIC_CURRENT i
    RANGE g, e
}

UNITS {
    (S) = (siemens)
    (mV) = (millivolt)
}

PARAMETER {
    g = 0.0001 (S/cm2)
    e = -65 (mV)
}

ASSIGNED {
    v (mV)
    i (mA/cm2)
}

BREAKPOINT {
    i = g * (v - e)
}
