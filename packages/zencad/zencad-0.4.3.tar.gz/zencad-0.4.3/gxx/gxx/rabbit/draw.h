#ifndef GXX_RABBIT_DRAW_H
#define GXX_RABBIT_DRAW_H

#include <gxx/x11wrap/shower2d.h>
#include <gxx/rabbit/topo2.h>

namespace rabbit {
	void draw(gxx::drawer2d& d, const loop2& l) {
		for(const auto& t : l.edges) {
			//gxx::println(typeid(*t.crv));
			if (typeid(*t.crv) == typeid(gxx::geom2::line)) {
				auto strt = t.start();
				auto stop = t.finish();
				d.add_line(strt.x, strt.y, stop.x, stop.y);
			}
			else if (typeid(*t.crv) == typeid(gxx::geom2::circle)) {
				gxx::println("draw circle!!!");

				double len = t.tparam.length();
				int n = len / (2*M_PI) * 50;
				double step = len / (n - 1);
				for (int i = 0;  i < n - 1; i++) {
					auto strt = t.crv->d0(t.tparam.minimum + i * step);
					auto stop = t.crv->d0(t.tparam.minimum + (i + 1) * step);
					d.add_line(strt.x, strt.y, stop.x, stop.y);
				}
			}
		}
	}
}

#endif