from __future__ import annotations

import gdsfactory as gf
from gdsfactory import cell
from gdsfactory.component import Component
from gdsfactory.routing.route_single import route_single
from gdsfactory.typings import ComponentSpec, CrossSectionSpec


@cell
def coh_tx_dual_pol(
    splitter: ComponentSpec = "mmi1x2",
    combiner: ComponentSpec | None = None,
    spol_coh_tx: ComponentSpec = "coh_tx_single_pol",
    yspacing: float = 10.0,
    xspacing: float = 40.0,
    input_coupler: ComponentSpec | None = None,
    output_coupler: ComponentSpec | None = None,
    cross_section: CrossSectionSpec = "xs_sc",
    **kwargs,
) -> Component:
    """Dual polarization coherent transmitter.

    Args:
        splitter: splitter function.
        combiner: combiner function.
        spol_coh_tx: function generating a coherent tx for a single polarization.
        yspacing: vertical spacing between each single polarization coherent tx.
        xspacing: horizontal spacing between splitter and combiner.
        input_coupler: Optional coupler to add before the splitter.
        output_coupler: Optional coupler to add after the combiner.
        cross_section: for routing (splitter to mzms and mzms to combiners).
        kwargs: cross_section settings.

     .. code::

                                 ___ single_pol_tx__
                                 |                  |
                                 |                  |
                                 |                  |
        (in_coupler)---splitter==|                  |==combiner---(out_coupler)
                                 |                  |
                                 |                  |
                                 |___ single_pol_tx_|
    """
    spol_coh_tx = gf.get_component(spol_coh_tx)

    # ----- Draw single pol coherent transmitters -----
    # Add MZM 1
    c = Component()

    single_tx_1 = c << spol_coh_tx
    single_tx_2 = c << spol_coh_tx

    # Separate the two receivers
    single_tx_2.d.movey(single_tx_1.d.ymin - yspacing - single_tx_2.d.ymax)

    # ------------ Splitters and combiners ---------------
    splitter = gf.get_component(splitter)
    sp = c << splitter
    sp.d.x = single_tx_1.d.xmin - xspacing
    sp.d.y = (single_tx_1.ports["o1"].d.y + single_tx_2.ports["o1"].d.y) / 2

    route = route_single(
        c,
        sp.ports["o2"],
        single_tx_1.ports["o1"],
        cross_section=cross_section,
        with_sbend=False,
        **kwargs,
    )

    route = route_single(
        c,
        sp.ports["o3"],
        single_tx_2.ports["o1"],
        cross_section=cross_section,
        with_sbend=False,
        **kwargs,
    )

    if combiner:
        combiner = gf.get_component(combiner)
        comb = c << combiner
        comb.mirror()

        comb.d.x = single_tx_1.d.xmax + xspacing
        comb.d.y = (single_tx_1.ports["o2"].d.y + single_tx_2.ports["o2"].d.y) / 2

        route = route_single(
            c,
            comb.ports["o2"],
            single_tx_1.ports["o2"],
            cross_section=cross_section,
            with_sbend=False,
            **kwargs,
        )
        c.add(route.references)

        route = route_single(
            c,
            comb.ports["o3"],
            single_tx_2.ports["o2"],
            cross_section=cross_section,
            with_sbend=False,
            **kwargs,
        )
        c.add(route.references)

    if input_coupler:
        in_coupler = gf.get_component(input_coupler)
        in_coup = c << in_coupler
        in_coup.connect("o1", sp.ports["o1"])

    else:
        c.add_port("o1", port=sp.ports["o1"])

    if output_coupler:
        output_coupler = gf.get_component(output_coupler)
        out_coup = c << output_coupler
        if combiner:
            # Add output coupler
            out_coup.connect("o1", comb.ports["o1"])
        else:
            # Directly connect the output coupler to the branches.
            # Assumes the output couplers has ports "o1" and "o2"

            out_coup.d.y = (single_tx_1.d.y + single_tx_2.d.y) / 2
            out_coup.d.xmin = single_tx_1.d.xmax + 40.0

            route = route_single(
                c,
                single_tx_1.ports["o2"],
                out_coup.ports["o1"],
                cross_section=cross_section,
                with_sbend=False,
                **kwargs,
            )

            route = route_single(
                c,
                single_tx_2.ports["o2"],
                out_coup.ports["o2"],
                cross_section=cross_section,
                with_sbend=False,
                **kwargs,
            )
    else:
        c.add_port("o2", port=single_tx_1.ports["o2"])
        c.add_port("o3", port=single_tx_2.ports["o2"])

    c.add_ports(single_tx_1.ports.filter(port_type="electrical"), prefix="pol1_")
    c.add_ports(single_tx_2.ports.filter(port_type="electrical"), prefix="pol2_")
    return c


if __name__ == "__main__":
    c = coh_tx_dual_pol()
    c.show()
