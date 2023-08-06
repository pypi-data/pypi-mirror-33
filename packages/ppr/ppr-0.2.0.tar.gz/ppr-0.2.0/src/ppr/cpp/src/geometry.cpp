#include "geometry.h"

#include <Eigen/Dense>
#include <iostream>
#include <math.h>

RotationMatrix create_rotation_matrix(double angle) {
    RotationMatrix R;
    R << cos(angle), -sin(angle),
         sin(angle),  cos(angle);
    return R;
}

Rectangle::Rectangle(double px, double py, double dx, double dy, double a) {
  // TODO turn around other point than left bottom corner
  width_ = dx;
  height_ = dy;
  pos_x_ = px;
  pos_y_ = py;
  rotation_matrix_ = create_rotation_matrix(a);
  tolerance_ = 1e-6;
}

void Rectangle::set_tolerance(double new_tolerance) {
    tolerance_ = new_tolerance;
}

void Rectangle::set_pose(double px, double py, double a) {
    pos_x_ = px;
    pos_y_ = py;
    rotation_matrix_ = create_rotation_matrix(a);
}

void Rectangle::set_size(double dx, double dy) {
    width_ = dx;
    height_ = dy;
}

std::vector<Vector2D> Rectangle::_get_vertices() {
    // Vector2Ds are ordered counterclockwise
    std::vector<Vector2D> points;
    points.push_back(Vector2D(pos_x_, pos_y_));
    points.push_back(rotation_matrix_ * Vector2D(width_, 0)      + points[0]);
    points.push_back(rotation_matrix_ * Vector2D(width_, height_) + points[0]);
    points.push_back(rotation_matrix_ * Vector2D(0, height_)     + points[0]);
    return points;
}

std::vector<Vector2D> Rectangle::_get_normals() {
    std::vector<Vector2D> normals;
    // Outside pointing normal ordered counterclockwise
    Vector2D n0(0, -1);
    Vector2D n1(1, 0);
    Vector2D n2(0, 1);
    Vector2D n3(-1, 0);
    // rotate normals to align with actual rectangle
    normals.push_back(rotation_matrix_ * n0);
    normals.push_back(rotation_matrix_ * n1);
    normals.push_back(rotation_matrix_ * n2);
    normals.push_back(rotation_matrix_ * n3);
    return normals;
}

std::vector<double> Rectangle::get_projection(Vector2D direction) {
    // direction is assumed to be a unit vector
    // therefore projecting is just taking the dot product
    std::vector<Vector2D> vert = _get_vertices();
    std::vector<double> proj;
    for (int i=0; i<4; ++i) {
        proj.push_back( direction.dot(vert[i]) );
    }
    return proj;
}

bool Rectangle::is_in_collision(Rectangle other) {
    std::vector<Vector2D> n1 = _get_normals();
    std::vector<Vector2D> n2 = other._get_normals();
    // Only check along two main normals of the two rectangles
    std::vector<Vector2D> normals_to_check = {n1[0], n1[1], n2[0], n2[1]};
    bool col = true;
    int i = 0;
    while (col and i < normals_to_check.size()) {
        std::vector<double> proj1 = get_projection(normals_to_check[i]);
        std::vector<double> proj2 = other.get_projection(normals_to_check[i]);
        double max1, max2, min1, min2;
        // calculate min and max
        max1 = *std::max_element(proj1.begin(), proj1.end());
        max2 = *std::max_element(proj2.begin(), proj2.end());
        min1 = *std::min_element(proj1.begin(), proj1.end());
        min2 = *std::min_element(proj2.begin(), proj2.end());
        if ((max1 + tolerance_ < min2) or (min1 > max2 + tolerance_)) {
            col = false;
        }
        ++i;
    }
    return col;
}

void Rectangle::get_vertices(double mat[4][2]) {
    std::vector<Vector2D> temp = _get_vertices();
    for (int i=0; i < temp.size(); ++i) {
        mat[i][0] = temp[i][0];
        mat[i][1] = temp[i][1];
    }
}

void Rectangle::get_normals(double mat[4][2]) {
    std::vector<Vector2D> temp = _get_normals();
    for (int i=0; i < temp.size(); ++i) {
        mat[i][0] = temp[i][0];
        mat[i][1] = temp[i][1];
    }
}