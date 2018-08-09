import tkinter as tk
from database import *
from settings import *


def pvp():
    global pve_flag
    pve_flag = False


def pve():
    global pve_flag
    pve_flag = True


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
                               width=LINE_WIDTH_UNCOLORED)
            line_label += 1


def events_bind(canvas):
    for i in range(0, 15):
        tag = "line" + str(i)
        canvas.tag_bind(tag, sequence="<Enter>", func=line_enter(canvas, i))
        canvas.tag_bind(tag, sequence="<Leave>", func=line_leave(canvas, i))
        canvas.tag_bind(tag, sequence="<Button-1>", func=change_line_color(canvas, i))


def line_enter(canvas, n):
    def enter(event):
        if STATUS[n] == UN_COLORED:
            canvas.itemconfig("line"+str(n), width=LINE_WIDTH_COLORED)
            get_next_prediction(n)
            update_prediction_text(canvas)
    return enter


def line_leave(canvas, n):
    def leave(event):
        if STATUS[n] == UN_COLORED:
            canvas.itemconfigure("line"+str(n), width=LINE_WIDTH_UNCOLORED)
        get_prediction()
        update_prediction_text(canvas)
    return leave


def ternary2ten(array):
    num_base10 = 0
    for i in range(15):
        num_base10 += int(array[i])*(3 ** i)
    return num_base10


def get_index(num):
    return (hash_dictionary[(num,)])[0]


def get_value(index):
    return value_database[index]


def get_remoteness(index):
    return remoteness_database[index]


def is_primitive(index):
    if get_remoteness(index) == 0:
        return True
    else:
        return False


def primitive(index):
    return get_value(index)


def lock_lines():
    for i in range(15):
        STATUS[i] = LOCKED


def get_current_value_and_remt():
    current_index = get_index(ternary2ten(ternary_num))
    current_value = get_value(current_index)
    current_remt = get_remoteness(current_index)
    return current_value, current_remt


def is_game_end():
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
#######################################################################################################################


def next_turn():
    global play1_flag
    play1_flag = not play1_flag


def change_line_color(canvas, n):
    def change_color(event):
        global play1_flag
        if STATUS[n] == UN_COLORED:
            if play1_flag:
                canvas.itemconfigure("line"+str(n), fill=COLOR1)
                STATUS[n] = COLOR1
                ternary_num[n] = '1'
                next_turn()
                is_game_end()
                if pve_flag:
                    computer_turn(canvas)
            else:
                canvas.itemconfigure("line"+str(n), fill=COLOR2)
                STATUS[n] = COLOR2
                ternary_num[n] = '2'
                next_turn()
                is_game_end()
        update_lines_color(canvas)
        get_prediction()
        update_prediction_text(canvas)
    return change_color


def get_hint_color(i):
    predict_ternary_num = ternary_num[:]  # copy
    # if play1_flag:
    predict_ternary_num[i] = '1' if play1_flag else '2'
    predict_ternary_num = ternary2ten(predict_ternary_num)
    index = get_index(predict_ternary_num)
    remoteness = get_remoteness(index)
    predict_value = get_value(index)
    return get_color_by_value(predict_value, remoteness)


def get_color_by_value(my_value, remoteness):
    remts_win_dict, remts_lose_dict = classify_remoteness()
    if my_value == "WIN":
        remts_num = len(remts_win_dict.keys())
        index = sorted(remts_win_dict.keys()).index(remoteness)
        return lose_colors[14*index//remts_num]
    elif my_value == "LOSE":
        index = sorted(remts_lose_dict.keys()).index(remoteness)
        remts_num = len(remts_lose_dict.keys())
        return win_colors[14*index//remts_num]


def classify_remoteness():
    remts_lose = {}
    remts_win = {}
    for i in range(15):
        if STATUS[i] == UN_COLORED:
            predict_ternary_num = ternary_num[:]  # copy
            predict_ternary_num[i] = '1' if play1_flag else '2'
            predict_ternary_num = ternary2ten(predict_ternary_num)
            index = get_index(predict_ternary_num)
            predict_value = get_value(index)
            predict_remt = get_remoteness(index)
            if predict_value == "WIN":
                if predict_remt not in remts_win:
                    remts_win[predict_remt] = []
                remts_win[predict_remt].append(i)
            elif predict_value == "LOSE":
                if predict_remt not in remts_lose:
                    remts_lose[predict_remt] = []
                remts_lose[predict_remt].append(i)
    return remts_win, remts_lose


def game_start(canvas, mode):
    def start():
        global play1_flag
        for i in range(15):
            canvas.itemconfig("line"+str(i), fill=UN_COLORED, width=LINE_WIDTH_UNCOLORED)
            ternary_num[i] = '0'  # reset the ternary num
            STATUS[i] = UN_COLORED
        play1_flag = True
        manage_hints(canvas)
        update_lines_color(canvas)
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
    canvas.create_text((700, 330), text=prediction, tags="hints_prediction", font="Times 16 bold")


def show_players(canvas):
    canvas.create_oval((50, 200), (75, 225), fill=COLOR1)
    canvas.create_oval((50, 250), (75, 275), fill=COLOR2)
    canvas.create_text((125, 213), text="Player1", font="Times 16 bold")
    canvas.create_text((125, 263), text="Player2", font="Times 16 bold")


def hide_hints(canvas):
    canvas.delete("hints")
    canvas.delete("hints_prediction")
    for i in range(15):
        if STATUS[i] == UN_COLORED:
            canvas.itemconfig("line"+str(i), fill=UN_COLORED)


def update_lines_color(canvas):
    if hints_flag:
        for i in range(15):
            if STATUS[i] == UN_COLORED:
                canvas.itemconfig("line" + str(i), fill=get_hint_color(i))
    else:
        hide_hints(canvas)


def update_prediction_text(canvas):
    canvas.itemconfig("hints_prediction", text=prediction)


def manage_hints(canvas):
    def hints():
        global hints_flag
        hints_flag = not hints_flag
        if hints_flag:
            get_prediction()
            show_hints(canvas)
        else:
            hide_hints(canvas)
        update_lines_color(canvas)
    return hints


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
        max_remt2lose = -1
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
    next_line_label = make_decision()
    canvas.itemconfigure("line" + str(next_line_label), fill=COLOR2, width=LINE_WIDTH_COLORED)
    STATUS[next_line_label] = COLOR2
    ternary_num[next_line_label] = '2'
    next_turn()
    get_prediction()
    is_game_end()


def get_prediction():
    global prediction
    current_value, current_remt = get_current_value_and_remt()
    if play1_flag:
        if current_value == "WIN":
            prediction = p1_name + " should\n win in " + str(current_remt)
        elif current_value == "LOSE":
            prediction = p1_name + " should\n lose in " + str(current_remt)
    else:
        if current_value == "WIN":
            prediction = p2_name + " should\n win in " + str(current_remt)
        elif current_value == "LOSE":
            prediction = p2_name + " should\n lose in " + str(current_remt)


def get_next_prediction(line_label):
    global prediction
    predict_ternary_num = ternary_num[:]
    if play1_flag:
        predict_ternary_num[line_label] = '1'
    else:
        predict_ternary_num[line_label] = '2'
    predict_index = get_index(ternary2ten(predict_ternary_num))
    predict_value = get_value(predict_index)
    predict_remt = get_remoteness(predict_index)
    if play1_flag:
        if predict_value == "LOSE":
            prediction = "If choose this\n" + p1_name + " should\n win in " + str(predict_remt)
        elif predict_value == "WIN":
            prediction = "If choose this\n" + p1_name + " should\n lose in " + str(predict_remt)
    else:
        if predict_value == "LOSE":
            prediction = "If choose this\n" + p2_name + " should\n win in " + str(predict_remt)
        elif predict_value == "WIN":
            prediction = "If choose this\n" + p2_name + " should\n lose in " + str(predict_remt)
