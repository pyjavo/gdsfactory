from __future__ import annotations

from functools import partial

from gdsfactory import cell
from gdsfactory.component import Component
from gdsfactory.components.compass import compass
from gdsfactory.components.via_stack import via_stack_slab_npp_m3
from gdsfactory.typings import ComponentSpec, Floats, LayerSpecs

pad_via_stack_slab_npp = partial(via_stack_slab_npp_m3, size=(80, 80))


@cell
def resistance_sheet(
    width: float = 10.0,
    layers: LayerSpecs = ("SLAB90", "NPP"),
    layer_offsets: Floats = (0, 0.2),
    pad: ComponentSpec = pad_via_stack_slab_npp,
    pad_size: tuple[float, float] = (50.0, 50.0),
    pad_pitch: float = 100.0,
    ohms_per_square: float | None = None,
    pad_port_name: int = "e4",
) -> Component:
    """Returns Sheet resistance.

    keeps connectivity for pads and first layer in layers

    Args:
        width: in um.
        layers: for the middle part.
        layer_offsets: from edge, positive: over, negative: inclusion.
        pad: function to create a pad.
        pad_pitch: in um.
        ohms_per_square: optional sheet resistance to compute info.resistance.
        port_orientation1: in degrees.
        port_orientation2: in degrees.
    """
    c = Component()

    pad = pad(size=pad_size)
    length = pad_pitch - pad_size[0]

    pad1 = c << pad
    pad2 = c << pad
    r0 = c << compass(
        size=(length + layer_offsets[0], width + layer_offsets[0]), layer=layers[0]
    )

    for layer, offset in zip(layers[1:], layer_offsets[1:]):
        _ = c << compass(size=(length + 2 * offset, width + 2 * offset), layer=layer)

    pad1.connect(
        "e3", r0.ports["e1"], allow_width_mismatch=True, allow_layer_mismatch=True
    )
    pad2.connect(
        "e1", r0.ports["e3"], allow_width_mismatch=True, allow_layer_mismatch=True
    )

    c.info["resistance"] = ohms_per_square * width * length if ohms_per_square else 0
    c.add_port(
        name="pad1",
        port=pad1.ports[pad_port_name],
    )
    c.add_port(
        name="pad2",
        port=pad2.ports[pad_port_name],
    )
    # c.add_port(
    #     name="pad1",
    #     port_type="vertical_dc",
    #     center=pad1.center,
    #     layer=list(layers)[-1],
    #     width=width,
    #     orientation=port_orientation1,
    # )
    # c.add_port(
    #     name="pad2",
    #     port_type="vertical_dc",
    #     center=pad2.center,
    #     layer=list(layers)[-1],
    #     width=width,
    #     orientation=port_orientation2,
    # )
    # c.absorb(pad1)
    # c.absorb(pad2)
    return c


if __name__ == "__main__":
    # import gdsfactory as gf
    # sweep = [resistance_sheet(width=width, layers=((1,0), (1,1))) for width in [1, 10, 100]]
    # c = gf.pack(sweep)[0]

    c = resistance_sheet()
    c.show()

    # import gdsfactory as gf
    # sweep_resistance = list(map(resistance_sheet, (5, 10, 80)))
    # c = gf.grid(sweep_resistance)
    # c.show( )
