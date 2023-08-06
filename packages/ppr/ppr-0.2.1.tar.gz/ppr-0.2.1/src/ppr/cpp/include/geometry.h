#ifndef _GEOMETRY_H_
#define _GEOMETRY_H_

#include <Eigen/Dense>
#include <vector>

typedef Eigen::Matrix2f RotationMatrix;
typedef Eigen::Vector2f Vector2D;

const double PI = 3.141592653589793238462643383279502884L;

/** Create 2D rotation matrix from given angle.
*/
RotationMatrix create_rotation_matrix(double angle);

/** Rectanlge representation and collision checking
 */
class Rectangle {
    double width_, height_, pos_x_, pos_y_; /**< size and position */
    double tolerance_;                      /**< minimum distance for collision checking */
    RotationMatrix rotation_matrix_;        /**< orientation of rectangle, rotation around corner */
    std::vector<Vector2D> _get_vertices();
    std::vector<Vector2D> _get_normals();
    /** Project vertices on axis perpendicular to given direction
     * */
    std::vector<double> get_projection(Vector2D direction);

  public:
    Rectangle(double, double, double, double, double);
    void set_tolerance(double new_tolerance);
    void set_pose(double px, double py, double a);
    void set_size(double dx, double dy);
    bool is_in_collision(Rectangle other);
    void get_vertices(double mat[4][2]);
    void get_normals(double mat[4][2]);
};

#endif