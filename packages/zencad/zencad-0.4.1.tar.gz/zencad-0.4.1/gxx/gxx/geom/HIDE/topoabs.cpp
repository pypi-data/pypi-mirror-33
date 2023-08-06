#include <gxx/geom/topoabs.h>
#include <gxx/geom/project.h>

namespace gxx {
	namespace topo {
		/*curve2 curve3::project_line_to(const surface& surf) {
			gxx::println("project line to surface");
			switch (surf.type) {
				case surface_enum::plane:
					return gxx::topo::project_line_to_plane(as_line(), surf.as_plane(), tmax);
				default: gxx::panic("project_line_to: undefined surface");
			}
		}

		curve2 curve3::project_to(const surface& surf) {
			switch (type) {
				case curve3_enum::line: return project_line_to(surf);
				default: gxx::panic("project_to: undefined curve");
			}
		}*/
	}
} 