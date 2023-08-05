namespace MPC {
    #include "MPC2860.h"
}

// 1. auto_set
static int auto_set() {
    return MPC::auto_set();
}

// 2. init_board
static int init_board() {
    return MPC::init_board();
}

// 3. set_el_logic
static int set_el_logic(int ch, int mode) {
    return MPC::set_el_logic(ch, mode);
}

// 4. set_org_logic
static int set_org_logic(int ch, int mode) {
    return MPC::set_org_logic(ch, mode);
}

// 5. set_alm_logic
static int set_alm_logic(int ch, int mode) {
    return MPC::set_alm_logic(ch, mode);
}

// 6. set_maxspeed
static int set_maxspeed(int ch, double speed) {
    return MPC::set_maxspeed(ch, speed);
}

// 7. set_conspeed
static int set_conspeed(int ch, double conspeed) {
    return MPC::set_conspeed(ch, conspeed);
}

// 8. set_profile
static int set_profile(int ch, double vl, double vh, double ad, double dc) {
    return MPC::set_profile(ch, vl, vh, ad, dc);
}

// 9. sudden_stop
static int sudden_stop(int ch) {
    return MPC::sudden_stop(ch);
}

// 10. check_done
static int check_done(int ch) {
    return MPC::check_done(ch);
}

// 11. con_pmove
static int con_pmove(int ch, double step) {
    return MPC::con_pmove(ch, step);
}

// 12. con_hmove
static int con_hmove(int ch, int dir) {
    return MPC::con_hmove(ch, dir);
}

// 13. get_abs_pos
static double get_abs_pos(int ch) {
    double pos;
    MPC::get_abs_pos(ch, &pos);
    return pos;
}

// 14. get_encoder
static long get_encoder(int ch) {
    long count;
    MPC::get_encoder(ch, &count);
    return count;
}

// 15. reset_pos
static int reset_pos(int ch) {
    return MPC::reset_pos(ch);
}

// 16. set_encoder
static int set_encoder(int ch, long count) {
    return MPC::set_encoder(ch, count);
}
