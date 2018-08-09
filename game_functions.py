import tkinter as tk
from database import *
dots = [(400, 50),  (573, 150), (573, 350), (400, 450), (227, 350), (227, 150)]
UN_COLORED = "gray"
COLOR1 = "blue"
COLOR2 = "orange"
# COLOR_LOSE = "red"
# COLOR_WIN = "green"
win_colors = ["#00ff00", "#08ff08", "#10ff10", "#18ff18", "#20ff20", "#28ff28", "#30ff30", "#38ff38", "#40ff40", \
              "#48ff48", "#50ff50", "#58ff58", "#60ff60", "#68ff68", "#70ff70"]
lose_colors = ["#ff0000", "#ff0808", "#ff1010", "#ff1818", "#ff2020", "#ff2828", "#ff3030", "#ff3838", "#ff4040", \
               "#ff4848", "#ff5050", "#ff5858", "#ff6060", "#ff6868", "#ff7070"]
LOCKED = ""
STATUS = [UN_COLORED for i in range(15)]  # STATUS: gray, blue, orange
play1_flag = True
hints_flag = False
ternary_num = ['0' for x in range(15)]  # 15bit
pve_flag = False
p1_name = "p1"
p2_name = "p2"
prediction = ""


def pvp():
    global pve_flag
    pve_flag = False


def pve():
    global pve_flag
    pve_flag = True


def line_enter(canvas, n):
    def enter(event):
        if STATUS[n] == UN_COLORED:
            canvas.itemconfig("line"+str(n), width=6)
    return enter


def line_leave(canvas, n):
    def leave(event):
        if STATUS[n] == UN_COLORED:
            canvas.itemconfigure("line"+str(n), width=3)
    return leave


def change_line_color(canvas, n):
    def change_color(event):
        global play1_flag
        global prediction
        if STATUS[n] == UN_COLORED:
            if play1_flag:
                canvas.itemconfigure("line"+str(n), fill=COLOR1)
                STATUS[n] = COLOR1
                ternary_num[n] = '1'
                play1_flag = not play1_flag
                get_prediction()
                show_result()
                if pve_flag:
                    computer_turn(canvas)
            else:
                canvas.itemconfigure("line"+str(n), fill=COLOR2)
                STATUS[n] = COLOR2
                ternary_num[n] = '2'
                play1_flag = not play1_flag
                show_result()
        update_lines_color(canvas)
    return change_color


def get_hint_color(i):
    predict_ternary_num = ternary_num[:]  # copy
    if play1_flag:
        predict_ternary_num[i] = '1'
        predict_ternary_num = ternary2ten(predict_ternary_num)
        index = get_index(predict_ternary_num)
        remoteness = get_remoteness(index)
        predict_value = get_value(index)
        return get_color_by_value(predict_value, remoteness)
    else:
        predict_ternary_num[i] = '2'
        predict_ternary_num = ternary2ten(predict_ternary_num)
        index = get_index(predict_ternary_num)
        remoteness = get_remoteness(index)
        predict_value = get_value(index)
        return get_color_by_value(predict_value, remoteness)


def get_color_by_value(my_value, remoteness):
    if my_value == "WIN":
        return lose_colors[remoteness]
    elif my_value == "LOSE":
        return win_colors[remoteness]


def draw_lines(canvas):
    line_label = 0
    for i in range(0, 6):
        dot1 = dots[i]
        for j in range(i + 1, 6):
            dot2 = dots[j]
            canvas.create_line(dot1,
                               dot2,
                               tags=("line" + str(line_label)),
                               fill=UN_COLORED,
                               width=3)
            line_label += 1


def events_bind(canvas):
    for i in range(0, 15):
        tag = "line" + str(i)
        canvas.tag_bind(tag, sequence="<Enter>", func=line_enter(canvas, i))
        canvas.tag_bind(tag, sequence="<Leave>", func=line_leave(canvas, i))
        canvas.tag_bind(tag, sequence="<Button-1>", func=change_line_color(canvas, i))


def game_start(canvas, mode):
    def start():
        global play1_flag
        for i in range(15):
            canvas.itemconfig("line"+str(i), fill=UN_COLORED, width=3)
            ternary_num[i] = '0'  # reset the ternary num
            STATUS[i] = UN_COLORED
        play1_flag = True
        manage_hints(canvas)
        game_mode = mode
        if game_mode == "pvp":
            pvp()
        elif game_mode == "pve":
            pve()
    return start


def show_hints(canvas):
    canvas.create_oval((650, 200), (675, 225), tags="hints", fill="green")
    canvas.create_oval((650, 250), (675, 275), tags="hints", fill="red")
    canvas.create_text((700, 213), text="WIN", tags="hints", font="Times 16 bold")
    canvas.create_text((710, 263), text="LOSE", tags="hints", font="Times 16 bold")
    canvas.create_text((650, 300), text=prediction, tags="hints", font="Times 16 bold")


def hide_hints(canvas):
    canvas.delete("hints")
    for i in range(15):
        if STATUS[i] == UN_COLORED:
            canvas.itemconfig("line"+str(i), fill=UN_COLORED)


def get_index(num):
    return (hash_dictionary[(num,)])[0]


def get_value(index):
    return value_database[index]


def get_remoteness(index):
    return remoteness_database[index]


def update_lines_color(canvas):
    if hints_flag:
        for i in range(15):
            if STATUS[i] == UN_COLORED:
                canvas.itemconfig("line" + str(i), fill=get_hint_color(i))
    else:
        hide_hints(canvas)


def manage_hints(canvas):
    def hints():
        global hints_flag
        hints_flag = not hints_flag
        if hints_flag:
            show_hints(canvas)
        else:
            hide_hints(canvas)
        get_prediction()
        update_lines_color(canvas)
    return hints


def is_primitive(index):
    if get_remoteness(index) == 0:
        return True
    else:
        return False


def primitive(index):
    return get_value(index)


def show_result():
    index = get_index(ternary2ten(ternary_num))
    if is_primitive(index):
        primitive_value = primitive(index)
        top = tk.Toplevel()
        top.geometry("200x150")
        top.resizable(width=False, height=False)
        result_text = None
        top.title("Result")
        if primitive_value == "WIN":
            if play1_flag:
                result_text = tk.Label(top, width=200, height=150, font="Times 16 bold", text=p1_name+" win")
            else:
                result_text = tk.Label(top, width=200, height=150, font="Times 16 bold", text=p2_name+" win")
        elif primitive_value == "LOSE":
            if play1_flag:
                result_text = tk.Label(top, width=200, height=150, font="Times 16 bold", text=p2_name+" win")
            else:
                result_text = tk.Label(top, width=200, height=150, font="Times 16 bold", text=p1_name+" win")
        lock_lines()
        result_text.pack()
        top.mainloop()


def lock_lines():
    for i in range(15):
        STATUS[i] = LOCKED


def get_current_value_and_remt():
    current_index = get_index(ternary2ten(ternary_num))
    current_value = get_value(current_index)
    current_remt = get_remoteness(current_index)
    return current_value, current_remt


def make_decision():
    current_index = get_index(ternary2ten(ternary_num))
    current_value = get_value(current_index)
    if current_value == "WIN":
        min_remt2win = 999
        next_line_label = 0
        for i in range(15):
            if STATUS[i] == UN_COLORED:
                predict_ternary_num = ternary_num[:]  # copy
                predict_ternary_num[i] = '2'
                predict_ternary_num = ternary2ten(predict_ternary_num)
                index = get_index(predict_ternary_num)
                predict_value = get_value(index)
                if predict_value == "LOSE":
                    predict_remt = get_remoteness(index)
                    if min_remt2win > predict_remt:
                        min_remt2win = predict_remt
                        next_line_label = i
        return next_line_label
    elif current_value == "LOSE":
        max_remt2lose = 0
        next_line_label = 0
        for i in range(15):
            if STATUS[i] == UN_COLORED:
                predict_ternary_num = ternary_num[:]  # copy
                predict_ternary_num[i] = '2'
                predict_ternary_num = ternary2ten(predict_ternary_num)
                index = get_index(predict_ternary_num)
                predict_remt = get_remoteness(index)
                if max_remt2lose < predict_remt:
                    max_remt2lose = predict_remt
                    next_line_label = i
        return next_line_label


def computer_turn(canvas):
    global play1_flag
    next_line_label = make_decision()
    canvas.itemconfigure("line" + str(next_line_label), fill=COLOR2, width=6)
    STATUS[next_line_label] = COLOR2
    ternary_num[next_line_label] = '2'
    play1_flag = not play1_flag
    get_prediction()
    show_result()


def ternary2ten(array):
    num_base10 = 0
    for i in range(15):
        num_base10 += int(array[i])*(3 ** i)
    return num_base10


def get_prediction():
    global prediction
    current_value, current_remt = get_current_value_and_remt()
    if play1_flag:
        if current_value == "WIN":
            prediction = p1_name + "should win in " + str(current_remt)
        elif current_value == "LOSE":
            prediction = p2_name + "should win in " + str(current_remt)
    else:
        if current_value == "WIN":
            prediction = p1_name + "should win in " + str(current_remt)
        elif current_value == "LOSE":
            prediction = p1_name + "should win in " + str(current_remt)
'''
def get_names():
    names = ()
    return names


def input_names_pvp(master):
    top = tk.Toplevel()
    top.title("Your Name")
    p1name_text = tk.Text("Player1's Name")
    p2name_text = tk.Text("Player2's Name")
    verify_button = tk.Button(top,
                              text="OK",
                              font="Times 16 bold")


    # p1name_text.pack()
    # p2name_text.pack()
    # verify_button.pack()
    # top.mainloop()


def input_names_pve():
    top = tk.Toplevel()
    top.title("Your Name")
    tk.Text("Your Name")
'''