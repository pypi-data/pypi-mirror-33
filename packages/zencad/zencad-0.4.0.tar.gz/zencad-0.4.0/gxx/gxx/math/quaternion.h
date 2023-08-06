#ifndef GXX_QUATERNION_H
#define GXX_QUATERNION_H

#include <math.h>
#include <gxx/print.h>

#include <gxx/math/malgo3.h>

namespace malgo {
	template<typename T>
	class quaternion {
	public:
		T q0, q1, q2, q3;
		quaternion() : q0(1), q1(0), q2(0), q3(0) {}
		quaternion(T q0, T q1, T q2, T q3) : q0(q0), q1(q1), q2(q2), q3(q3) {}

		double abs() {
			return sqrt(q0*q0 + q1*q1 + q2*q2 + q3*q3);
		}

		void self_normalize() {
			double mod = abs();
			q0 /= mod;
			q1 /= mod;
			q2 /= mod;
			q3 /= mod;
		}

		/*quaternion normalize() {
			quaternion oth = *this;
			oth.self_normalize();
			return oth;
		}*/

		/*quaternion small_rotate1(T angle) {
			angle /= 2;
			auto nq = quaternion(
				q0 - q1 * angle,
				q1 + q0 * angle,
				q2 - q3 * angle,
				q3 + q2 * angle
			);
			nq.self_normalize();
			return nq;
		}

		quaternion small_rotate2(T angle) {
			angle /= 2;
			auto nq = quaternion(
				q0 - q2 * angle,
				q1 + q3 * angle,
				q2 + q0 * angle,
				q3 - q1 * angle
			);
			nq.self_normalize();
			return nq;
		}

		quaternion small_rotate3(T angle) {
			angle /= 2;
			auto nq = quaternion(
				q0 - q3 * angle,
				q1 - q2 * angle,
				q2 + q1 * angle,
				q3 + q0 * angle
			);
			nq.self_normalize();
			return nq;
		}*/

		void self_small_rotate1(T angle) {
			angle /= 2;
			T nq0 =	q0 - q1 * angle;
			T nq1 =	q1 + q0 * angle;
			T nq2 =	q2 - q3 * angle;
			T nq3 =	q3 + q2 * angle;
			q0 = nq0;
			q1 = nq1;
			q2 = nq2;
			q3 = nq3;
			self_normalize();
		}

		void self_small_rotate2(T angle) {
			angle /= 2;
			T nq0 =	q0 - q2 * angle;
			T nq1 =	q1 + q3 * angle;
			T nq2 =	q2 + q0 * angle;
			T nq3 =	q3 - q1 * angle;
			q0 = nq0;
			q1 = nq1;
			q2 = nq2;
			q3 = nq3;
			self_normalize();
		}

		void self_small_rotate3(T angle) {
			angle /= 2;
			T nq0 =	q0 - q3 * angle;
			T nq1 =	q1 - q2 * angle;
			T nq2 =	q2 + q1 * angle;
			T nq3 =	q3 + q0 * angle;
			q0 = nq0;
			q1 = nq1;
			q2 = nq2;
			q3 = nq3;
			self_normalize();
		}

		matrix3<T> rotation_matrix() {
			T qww = q0 * q0;
			T qxx = q1 * q1;
			T qyy = q2 * q2;
			T qzz = q3 * q3;
			T qxw = q1 * q0;
			T qyw = q2 * q0;
			T qzw = q3 * q0;
			T qxy = q1 * q2;
			T qxz = q1 * q3;
			T qyz = q2 * q3;
	
			return matrix3<T>(
				1 - 2*qyy - 2*qzz,		2*qxy - 2*qzw,			2*qxz + 2*qyw,
				2*qxy + 2*qzw,			1 - 2*qxx - 2*qzz,		2*qyz - 2*qxw,
				2*qxz - 2*qyw,			2*qyz + 2*qxw,			1 - 2*qxx - 2*qyy
			);
		}

		vector3<T> operator*(vector3<T> other) {
			return rotation_matrix() * other;
		}

		quaternion operator*(quaternion other) {
			return quaternion(
				+q0 * other.q0 - q1 * other.q1 - q2 * other.q2 - q3 * other.q3,
				+q0 * other.q1 + q1 * other.q0 + q2 * other.q3 - q3 * other.q2,
				+q0 * other.q2 - q1 * other.q3 + q2 * other.q0 + q3 * other.q1,
				+q0 * other.q3 + q1 * other.q2 - q2 * other.q1 + q3 * other.q0
			);		
		}

		size_t printTo(gxx::io::ostream& o) const {	
			return gxx::fprint_to(o, "({},{},{},{})", q0, q1, q2, q3); 
		}
	};
}

/*class quaternion:
	def __init__(self, q0=1, q1=0, q2=0, q3=0):
		#self.arr = np.array([q0,q1,q2,q3])
		self.q0, self.q1, self.q2, self.q3 = q0, q1, q2, q3

	def abs(self):
		return math.sqrt(self.q0**2+self.q1**2+self.q2**2+self.q3**2)

	def self_normalize(self):
		mod = self.abs()
		self.q0 = self.q0 / mod
		self.q1 = self.q1 / mod
		self.q2 = self.q2 / mod
		self.q3 = self.q3 / mod

	#def normalize(self):
	#	return quaternion(*(self.arr / np.linalg.norm(self.arr)))

	def self_snormalize(self):
		self.q0 = math.sqrt(1 - self.q1 ** 2 + self.q2 ** 2 + self.q3 ** 2)

	def __repr__(self):
		return (self.q0,self.q1,self.q2,self.q3).__repr__()

	def mul(self, other):
		return quaternion(
			+self.q0*other.q0 -self.q1*other.q1 -self.q2*other.q2 -self.q3*other.q3,
			+self.q0*other.q1 +self.q1*other.q0 +self.q2*other.q3 -self.q3*other.q2,
			+self.q0*other.q2 -self.q1*other.q3 +self.q2*other.q0 +self.q3*other.q1,
			+self.q0*other.q3 +self.q1*other.q2 -self.q2*other.q1 +self.q3*other.q0			
		)

	#def rotate_vector(self, x,y,z):
	#	q01 = self.q0*self.q1
	#	q02 = self.q0*self.q2
	#	q03 = self.q0*self.q3
	#	
	#	q11 = self.q1*self.q1
	#	q22 = self.q2*self.q2
	#	q33 = self.q3*self.q3
	#	
	#	q12 = self.q1*self.q2
	#	q13 = self.q1*self.q3
	#	q23 = self.q2*self.q3
	#	
	#	return (
	#		x * (1-2*q22-2*q33) 	+ y * 2*(q12+q03) 			+ z * 2*(q13+q02),
	#		x * 2*(q12+q03)			+ y * (1 - 2*q11 - 2*q33) 	+ z * 2*(q23+q01),
	#		x * 2*(q13+q02)	 		+ y * 2*(q23+q01) 			+ z * (1 - 2*q11- 2*q22),
	#	)

	def rotation_matrix(self):
		qww = self.q0 * self.q0
		qxx = self.q1 * self.q1
		qyy = self.q2 * self.q2
		qzz = self.q3 * self.q3

		qxw = self.q1 * self.q0
		qyw = self.q2 * self.q0
		qzw = self.q3 * self.q0

		qxy = self.q1 * self.q2
		qxz = self.q1 * self.q3

		qyz = self.q2 * self.q3


		mat = np.array([
			[1 - 2*qyy - 2*qzz,		2*qxy - 2*qzw,			2*qxz + 2*qyw],
			[2*qxy + 2*qzw,			1 - 2*qxx - 2*qzz,		2*qyz - 2*qxw],
			[2*qxz - 2*qyw,			2*qyz + 2*qxw,			1 - 2*qxx - 2*qyy]
		])
		return mat

	#res.q0 = a.q0 * b.q0 - a.q1 * b.q1 - a.q2 * b.q2 - a.q3 * b.q3
	#res.q1 = a.q0 * b.q1 + a.q1 * b.q0 + a.q2 * b.q3 - a.q3 * b.q2
	#res.q2 = a.q0 * b.q2 - a.q1 * b.q3 + a.q2 * b.q0 + a.q3 * b.q1
	#res.q3 = a.q0 * b.q3 + a.q1 * b.q2 - a.q2 * b.q1 + a.q3 * b.q0

	def small_rotate1(self, angle):
		#mod = 1/math.sqrt(1 + angle*angle)
		angle /= 2
		nq = quaternion(
			self.q0 - self.q1 * angle,
			self.q1 + self.q0 * angle,
			self.q2 - self.q3 * angle,
			self.q3 + self.q2 * angle
		)
		nq.self_normalize()
		return nq

	def small_rotate2(self, angle):
		angle /= 2
		nq = quaternion(
			self.q0 - self.q2 * angle,
			self.q1 + self.q3 * angle,
			self.q2 + self.q0 * angle,
			self.q3 - self.q1 * angle
		)
		nq.self_normalize()
		return nq


	def small_rotate3(self, angle):
		#mod = 1/math.sqrt(1 + angle*angle)
		angle /= 2
		nq = quaternion(
			self.q0 - self.q3 * angle,
			self.q1 - self.q2 * angle,
			self.q2 + self.q1 * angle,
			self.q3 + self.q0 * angle
		)
		nq.self_normalize()
		return nq
	

	def euler(self):
		return (
			math.atan2(2*(self.q0*self.q1 + self.q2*self.q3), 1-2*(self.q1**2 + self.q2**2)),
			math.asin(2*(self.q0*self.q2-self.q3*self.q1)),
			math.atan2(2*(self.q0*self.q3 + self.q1*self.q2), 1-2*(self.q2**2 + self.q3**2)),
		)
*/

#endif