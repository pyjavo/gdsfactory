from __future__ import annotations

from functools import partial

import gdsfactory as gf
from gdsfactory.name import clean_name
from gdsfactory.snap import snap_to_grid as snap
from gdsfactory.typings import Layer

ignore = (
    "cross_section",
    "decorator",
    "cross_section1",
    "cross_section2",
    "contact",
    "pad",
)
prefix_to_type_default = {
    "opt": "OPTICALPORT",
    "pad": "ELECTRICALPORT",
    "vertical_dc": "ELECTRICALPORT",
    "optical": "OPTICALPORT",
    "loopback": "OPTICALPORT",
}


def add_label_ehva(
    component: gf.Component,
    die: str = "demo",
    prefix_to_type: dict[str, str] = prefix_to_type_default,
    layer: Layer = (66, 0),
    metadata_ignore: list[str] | None = None,
    metadata_include_parent: list[str] | None = None,
    metadata_include_child: list[str] | None = None,
) -> gf.Component:
    """Returns Component with measurement labels.

    Args:
        component: to add labels to.
        die: string.
        port_types: list of port types to label.
        layer: text label layer.
        metadata_ignore: list of settings keys to ignore.
            Works with flatdict setting:subsetting.
        metadata_include_parent: includes parent metadata.
            Works with flatdict setting:subsetting.

    """
    metadata_ignore = metadata_ignore or []
    metadata_include_parent = metadata_include_parent or []
    metadata_include_child = metadata_include_child or []

    text = f"""DIE NAME:{die}
CIRCUIT NAME:{component.name}
"""
    info = []

    metadata = component.settings
    if metadata:
        info += [
            f"CIRCUITINFO NAME: {k}, VALUE: {v}"
            for k, v in metadata
            if k not in metadata_ignore and isinstance(v, int | float | str)
        ]

    metadata = component.settings
    info += [
        f"CIRCUITINFO NAME: {clean_name(k)}, VALUE: {metadata.get(k)}"
        for k in metadata_include_parent
        if metadata.get(k)
    ]

    metadata = component.settings
    info += [
        f"CIRCUITINFO NAME: {k}, VALUE: {metadata.get(k)}"
        for k in metadata_include_child
        if metadata.get(k)
    ]

    text += "\n".join(info)
    text += "\n"

    info = []
    if component.ports:
        for prefix, port_type_ehva in prefix_to_type.items():
            info += [
                f"{port_type_ehva} NAME: {port.name} TYPE: {port_type_ehva}, "
                f"POSITION RELATIVE:({snap(port.x)}, {snap(port.y)}),"
                f" ORIENTATION: {port.orientation}"
                for port in component.get_ports_list(prefix=prefix)
            ]
    text += "\n".join(info)

    component.add_label(text=text, position=(0, 0), layer=layer)
    return component


if __name__ == "__main__":
    add_label_ehva_demo = partial(
        add_label_ehva,
        die="demo_die",
        metadata_include_parent=["grating_coupler:settings:polarization"],
    )

    c = gf.c.straight(length=11)
    c = gf.c.mmi2x2(length_mmi=2.2)
    c = gf.routing.add_fiber_array(
        c,
        grating_coupler=gf.c.grating_coupler_te,
    )
    c = add_label_ehva(c)

    # add_label_ehva(c, die="demo_die", metadata_include_child=["width_mmi"])
    # add_label_ehva(c, die="demo_die", metadata_include_child=[])

    c.show()
