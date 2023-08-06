#ifndef GXX_GEOMETRIC_H
#define GXX_GEOMETRIC_H

#include "linalg.h"
using namespace linalg::aliases;

//Для представления плоскости (объект plane) используется 4д вектор, первые три параметра которого задают нормаль, а четвертый - параметр плоскости (расстояние до плоскости от начала координат).

namespace geometric {

	inline float3 trinormal(const float3& v0, const float3& v1, const float3& v2) {
		float3 cp = cross(v1 - v0, v2 - v1);
		float m = length(cp);
		if (m == 0) return float3(0, 0, 1);
		return cp*(1.0f / m);
	}

	// plane of triangle with vertex positions v0, v1, and v2
	// Строит плоскость через определение нормали и расчет параметра методом проецирования вершины на номаль.
	inline float4 plane_of(const float3 &v0, const float3 &v1, const float3 &v2) {
		auto n = trinormal(v0, v1, v2);
		return{ n, -dot(n,v0) };
	}


	inline float3 gradient(const float3 &v0, const float3 &v1, const float3 &v2,
		const float t0, const float t1, const float t2) {
		float3 e0 = v1 - v0;
		float3 e1 = v2 - v0;
		float  d0 = t1 - t0;
		float  d1 = t2 - t0;
		float3 pd = e1*d0 - e0*d1;
		if (pd == float3(0, 0, 0)){
			return float3(0, 0, 1);
		}
		pd = normalize(pd);
		if (fabsf(d0)>fabsf(d1)) {
			e0 = e0 + pd * -dot(pd, e0);
			e0 = e0 * (1.0f / d0);
			return e0 * (1.0f / dot(e0, e0));;
		}
		// else
		//assert(fabsf(d0) <= fabsf(d1));
		e1 = e1 + pd * -dot(pd, e1);
		e1 = e1 * (1.0f / d1);
		return e1 * (1.0f / dot(e1, e1));
	}

}

#endif