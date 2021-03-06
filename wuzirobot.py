# coding=utf-8
from robotcontrol import *
from utils.logger import logger
import numpy as np

# tangent of camera cone
# x_tan = (0.1882 / 0.264)
# y_tan = (0.1407 / 0.264)
x_tan = (0.3145 / 0.61146)
y_tan = (0.2276 / 0.61146)

x_tan = (-0.3081872 / 0.61146)
y_tan = (-0.23820488 / 0.61146)

x_tan = (-0.3543237 / 0.61146)
y_tan = (-0.20480625 / 0.61146)

x_tan = (-0.3590276 / 0.61146)
y_tan = (-0.22420567 / 0.61146)


class WuziRobot(Auboi5Robot):
    def __init__(self, logger):
        Auboi5Robot.__init__(self)
        self.logger = logger
        self.zero_radian = (0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000)
        self.init_pos = (-0.2863222836800378, -0.3641882948297106, 0.6854579419026046)
        self.init_ori = (0., 1., 0., 0.)
        self.zero_z = 0.182

        self.hello_position = (
            0.6351768374443054, 0.2261800915002823, -0.46258947253227234, -0.513762354850769, -1.3836095333099365,
            -0.9316167831420898)

    def prepare(self, ip='192.168.1.1', port=8899):
        # 创建并打印上下文
        handle = self.create_context()
        self.logger.info("robot.rshd={0}".format(handle))
        result = self.connect(ip, port)

        if result != RobotErrorType.RobotError_SUCC:
            self.logger.info("connect server{0}:{1} failed.".format(ip, port))
            raise RobotErrorType.RobotError_NotLogin
        else:
            # # 重新上电
            # self.robot_shutdown()
            #
            # # 上电
            # self.robot_startup()
            #
            # # 设置碰撞等级
            # self.set_collision_class(7)

            # 设置工具端电源为１２ｖ
            # self.set_tool_power_type(RobotToolPowerType.OUT_12V)

            # 设置工具端ＩＯ_0为输出
            self.set_tool_io_type(RobotToolIoAddr.TOOL_DIGITAL_IO_0, RobotToolDigitalIoDir.IO_OUT)

            # 获取工具端ＩＯ_0当前状态
            tool_io_status = self.get_tool_io_status(RobotToolIoName.tool_io_0)
            self.logger.info("tool_io_0={0}".format(tool_io_status))

            # 设置工具端ＩＯ_0状态
            self.set_tool_io_status(RobotToolIoName.tool_io_0, 1)

            # 获取控制柜用户DI
            io_config = self.get_board_io_config(RobotIOType.User_DI)

            # 输出DI配置
            self.logger.info(io_config)

            # 获取控制柜用户DO
            io_config = self.get_board_io_config(RobotIOType.User_DO)

            # 输出DO配置
            self.logger.info(io_config)

            # 当前机械臂是否运行在联机模式
            self.logger.info("self online mode is {0}".format(self.is_online_mode()))
            joint_status = self.get_joint_status()
            self.logger.info("joint_status={0}".format(joint_status))

            # 初始化全局配置文件
            self.init_profile()

            # 设置关节最大加速度
            self.set_joint_maxacc((1.5, 1.5, 1.5, 1.5, 1.5, 1.5))

            # 设置关节最大加速度
            self.set_joint_maxvelc((1.5, 1.5, 1.5, 1.5, 1.5, 1.5))
            # 获取关节最大加速度
            self.logger.info(self.get_joint_maxacc())

            self.logger.info(self.get_current_waypoint())
            self.set_tool_power_type(power_type=RobotToolPowerType.OUT_0V)
            print(0)

    def move_to_init(self):
        cur_x, cur_y, cur_z = self.current_waypoint['pos']
        if cur_z - self.zero_z < 0.05:
            ik_result = self.inverse_kin(self.current_waypoint['joint'], (cur_x, cur_y, self.zero_z + 0.05),
                                         self.current_waypoint['ori'])
            self.move_line(ik_result['joint'])
        logger.info("move to initial position")
        ik_result = self.inverse_kin(self.current_waypoint['joint'], self.init_pos, self.init_ori)
        self.move_joint(ik_result['joint'])

    def move_to_zero_ori(self):
        cur_x, cur_y, cur_z = self.current_waypoint['pos']
        # if cur_z - self.zero_z < 0.05:
        #     ik_result = self.inverse_kin(self.current_waypoint['joint'], (cur_x, cur_y, self.zero_z + 0.05),
        #                                  self.current_waypoint['ori'])
        #     self.move_line(ik_result['joint'])
        logger.info("move to zero ori")
        ik_result = self.inverse_kin(self.current_waypoint['joint'], (cur_x, cur_y, cur_z - 0.3), self.init_ori)
        if ik_result is None:
            print 'ik_result is None'
        else:
            self.move_joint(ik_result['joint'])

    def move_to_zero(self):
        logger.info("move to zero position")
        self.move_joint(self.zero_radian)

    def move_to_zero_z(self):
        dst_pos = list(self.current_waypoint['pos'])
        dst_pos[2] = self.zero_z
        ik_result = self.inverse_kin(self.current_waypoint['joint'], dst_pos, self.current_waypoint['ori'])
        self.move_joint(ik_result['joint'])

    @property
    def current_waypoint(self):
        return self.get_current_waypoint()

    # def move_to_coord(self, x, y):
    #     # cam coord - tool coord
    #     dx, dy = -0.008347545641425695, -0.02856086342482178
    #     # the angle between cam and tool
    #     deg = -0.02031323269453471
    #
    #     cur_x, cur_y, cur_z = self.current_waypoint['pos']
    #     cur_x = cur_x + dx
    #     cur_y = cur_y + dy
    #
    #     x = x - 320
    #     y = y - 240
    #     # rotate
    #     xy = np.matmul(np.array([[np.cos(deg), np.sin(deg)], [-np.sin(deg), np.cos(deg)]]), np.array([[x], [y]]))
    #     x = xy[0, 0]
    #     y = xy[1, 0]
    #
    #     cur_height = cur_z - self.zero_z + 0.104
    #     x_scale = cur_height * x_tan
    #     y_scale = cur_height * y_tan
    #     dst_x = cur_x - x*x_scale/320.
    #     dst_y = cur_y + y*y_scale/240.
    #
    #     ik_result = self.inverse_kin(self.current_waypoint['joint'], (dst_x, dst_y, self.zero_z), self.current_waypoint['ori'])
    #     self.move_joint(ik_result['joint'])

    def move_to_coord(self, x, y, lower=False):
        xf, yf = 0.3145, 0.2276
        x = (x - 320) / 320.
        y = (y - 240) / 240.

        cur_x, cur_y, cur_z = self.current_waypoint['pos']

        # intrinsic
        intri_mat = np.array([[-0.26025414, -0.11201902, 0.46335214],
                              [0.2190264, -0.07228895, 0.54456127],
                              [0.00456996, -0.23794995, 0.45977205]])
        R = np.array([[0.88068247, 0.00276375, 0.27867976],
                      [0.02697515, 1.04405, 0.38250926],
                      [-0.5211914, -0.6277767, 0.4366236]])
        t = np.array([-0.28089553, -0.3066029, 0.6314296])

        intri_mat = np.array([[-0.23469193, -0.12249327, 0.44167835],
                              [0.21669582, -0.07273288, 0.5128718],
                              [0.07611477, -0.2007165, 0.4141666]])
        R = np.array([[0.97371703, -0.10240156, 0.2761366],
                      [0.14718546, 1.0675778, 0.36602277],
                      [-0.38947088, -0.5786356, 0.44720966]])
        t = np.array([-0.30965808, -0.30189404, 0.6920944])

        # intri_mat = np.diag([xf, yf, 1])

        cam_x, cam_y, cam_z = np.matmul(intri_mat, np.array([x, -y, -0.61146]))

        dst_tool_coord = np.matmul(R, np.array([cam_x, cam_y, cam_z])) + t

        dst_x = dst_tool_coord[0] - cur_x
        dst_y = dst_tool_coord[1] - cur_y

        ik_result = self.inverse_kin(self.current_waypoint['joint'], (dst_x, dst_y, self.zero_z + 0.05),
                                     self.current_waypoint['ori'])
        self.move_joint(ik_result['joint'])
        if lower:
            zz = 0.02
        else:
            zz = 0.01
        ik_result = self.inverse_kin(self.current_waypoint['joint'], (dst_x, dst_y, self.zero_z - zz),
                                     self.current_waypoint['ori'])
        self.move_line(ik_result['joint'])

    def catch_chess(self, x, y):
        self.set_tool_power_type(power_type=RobotToolPowerType.OUT_0V)
        self.move_to_coord(x, y, lower=True)
        time.sleep(1)
        self.move_to_init()

    def release_chess(self, x, y):
        self.move_to_coord(x, y)
        self.set_tool_power_type(power_type=RobotToolPowerType.OUT_24V)
        time.sleep(1)
        self.move_to_init()
        self.set_tool_power_type(power_type=RobotToolPowerType.OUT_0V)

    def move_hello(self):
        logger.info("move to hello position")
        self.move_joint(self.hello_position)

    def write_name(self, ):
        pass

if __name__ == '__main__':
    # 系统初始化
    WuziRobot.initialize()

    # 创建机械臂控制类
    robot = WuziRobot(logger)
    try:
        robot.prepare()
        robot.set_tool_power_type(power_type=RobotToolPowerType.OUT_0V)
        import time

        time.sleep(5)
        robot.move_to_init()
        robot.move_to_zero_z()
        # robot.set_tool_power_type(power_type=RobotToolPowerType.OUT_24V)
        robot.move_to_init()
        robot.move_to_zero_z()
        robot.set_tool_power_type(power_type=RobotToolPowerType.OUT_24V)
        robot.move_to_init()

        # 断开服务器链接
        robot.disconnect()
    except RobotError, e:
        logger.error("{0} robot Event:{1}".format(robot.get_local_time(), e))

    finally:
        # 断开服务器链接
        if robot.connected:
            # 关闭机械臂
            robot.robot_shutdown()
            # 断开机械臂链接
            robot.disconnect()
        # 释放库资源
        Auboi5Robot.uninitialize()
        logger.info("{0} test completed.".format(Auboi5Robot.get_local_time()))
