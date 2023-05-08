import random
import json
import math

config = json.load(open('config.json', 'r'))

CHANGE_FREQ = min(config['cases']//20, 50)
SETTING = config['gen_setting']
LEN = SETTING['max_input']
MAX_NAME_LEN = 10
MAX_AGE = 200
MIN_VALUE = 1
MAX_VALUE = 100
MIN_MODIFY_VALUE = -100
MAX_MODIFY_VALUE = 100
MIN_SOCIAL_VALUE = -1000
MAX_SOCIAL_VALUE = 1000
USED_ID_PROB = 0.7
SAME_ID_PROB = 0.3

person_id = set()
group_id = set()
message_id = set()
cnt = 0


def to_rand_upper(s):
    return ''.join(random.choice([c.upper(), c]) for c in s)


def rand_name(maxlen=MAX_NAME_LEN):
    name = random.choices('abcdefghijklmnopqrstuvwxyz',
                          k=random.randint(1, maxlen))
    return to_rand_upper(''.join(name))


def rand_age():
    return random.randint(0, MAX_AGE)


def rand_value():
    return random.randint(MIN_VALUE, MAX_VALUE)


def rand_modify_value():
    return random.randint(MIN_MODIFY_VALUE, MAX_MODIFY_VALUE)


def rand_social_value():
    return random.randint(MIN_SOCIAL_VALUE, MAX_SOCIAL_VALUE)


def rand_id(used_id=person_id, same_id_prob=None):
    if same_id_prob is None:
        same_id_prob = USED_ID_PROB
    if len(used_id) == 0 or random.random() > same_id_prob:
        id = random.randint(-10000, 10000)
        used_id.add(id)
    else:
        id = random.choice(list(used_id))
    return id


"""
add_person id(int) name(String) age(int)
add_relation id(int) id(int) value(int)
query_value id(int) id(int)
query_circle id(int) id(int)
query_block_sum
query_triple_sum

add_group id(int)
add_to_group id(int) id(int)
del_from_group id(int) id(int)
query_group_value_sum id(int)
query_group_age_var id(int)
modify_relation id(int) id(int) value(int)
modify_relation_ok_test
query_best_acquaintance id(int)
query_couple_sum
add_message id(int) socialValue(int) type(int)
    person_id1(int) person_id2(int)|group_id(int)
send_message id(int)
query_social_value id(int)
query_received_messages id(int)

| name                    | inst |
| ----------------------- | ---- |
| add_person              | ap   |
| add_relation            | ar   |
| query_value             | qv   |
| query_circle            | qci  |
| query_block_sum         | qbs  |
| query_triple_sum        | qts  |
| add_group               | ag   |
| add_to_group            | atg  |
| del_from_group          | dfg  |
| query_group_value_sum   | qgvs |
| query_group_age_var     | qgav |
| modify_relation         | mr   |
| modify_relation_ok_test | mrok |
| query_best_acquaintance | qba  |
| query_couple_sum        | qcs  |
| add_message             | am   |
| send_message            | sm   |
| query_social_value      | qsv  |
| query_received_messages | qrm  |
"""


def gen_add_person():
    return f'ap {rand_id(same_id_prob=SAME_ID_PROB)} {rand_name()} {rand_age()}'


def gen_add_relation():
    return f'ar {rand_id()} {rand_id()} {rand_value()}'


def gen_query_value():
    return f'qv {rand_id()} {rand_id()}'


def gen_query_circle():
    return f'qci {rand_id()} {rand_value()}'


def gen_query_block_sum():
    return 'qbs'


def gen_query_triple_sum():
    return 'qts'


def gen_add_group():
    return f'ag {rand_id(group_id, same_id_prob=SAME_ID_PROB)}'


def gen_add_to_group():
    return f'atg {rand_id(group_id)} {rand_id()}'


def gen_del_from_group():
    return f'dfg {rand_id(group_id)} {rand_id()}'


def gen_query_group_value_sum():
    return f'qgvs {rand_id(group_id)}'


def gen_query_group_age_var():
    return f'qgav {rand_id(group_id)}'


def gen_modify_relation():
    return f'mr {rand_id()} {rand_id()} {rand_modify_value()}'


def gen_query_best_acquaintance():
    return f'qba {rand_id()}'


def gen_query_couple_sum():
    return 'qcs'


def gen_add_message():
    type = random.randint(0, 1)
    return f'am {rand_id(message_id, same_id_prob=SAME_ID_PROB)} {rand_social_value()} {type} ' + \
        f'{rand_id(person_id, same_id_prob=1)} ' + \
        f'{rand_id(group_id if type else person_id, same_id_prob=1)}'


def gen_send_message():
    return f'sm {rand_id(message_id)}'


def gen_query_social_value():
    return f'qsv {rand_id()}'


def gen_query_received_messages():
    return f'qrm {rand_id()}'


def op_normal():
    if random.random() < 0.3:
        return random.choice([ba_strong, message_strong,
                              group_strong, weak_strong, exception_strong])()
    ops = [gen_add_person] * 10
    ops += [gen_add_relation] * 15
    ops += [gen_query_value] * 1
    ops += [gen_query_circle] * 2
    ops += [gen_query_block_sum] * 1
    ops += [gen_query_triple_sum] * 1
    ops += [gen_add_group] * 6
    ops += [gen_add_to_group] * 8
    ops += [gen_del_from_group] * 3
    ops += [gen_query_group_value_sum] * 1
    ops += [gen_query_group_age_var] * 1
    ops += [gen_modify_relation] * 6
    ops += [gen_query_best_acquaintance] * 1
    ops += [gen_query_couple_sum] * 2
    ops += [gen_add_message] * 4
    ops += [gen_send_message] * 4
    ops += [gen_query_social_value] * 1
    ops += [gen_query_received_messages] * 1
    return ops


def set_global_prob(same_id_prob, used_id_prob):
    global SAME_ID_PROB, USED_ID_PROB
    SAME_ID_PROB = same_id_prob
    USED_ID_PROB = used_id_prob


def ba_strong():
    set_global_prob(0, 1)
    relation = random.randint(0, 5)
    ops = [gen_add_person] * 15
    ops += [gen_add_relation] * (5 + relation * 5)
    ops += [gen_modify_relation] * (5 + relation * 3)
    ops += [gen_query_best_acquaintance] * 1
    ops += [gen_query_couple_sum] * 1
    return ops


def message_strong():
    set_global_prob(0, 1)
    global MAX_MODIFY_VALUE
    MAX_MODIFY_VALUE = 10
    ops = [gen_add_person] * 8
    ops += [gen_add_relation] * 20
    ops += [gen_modify_relation] * 5 * random.randint(1, 4)
    ops += [gen_add_group] * 4
    ops += [gen_add_to_group] * 8
    ops += [gen_del_from_group] * 2
    ops += [gen_add_message] * 10
    ops += [gen_send_message] * 8
    ops += [gen_query_social_value] * 1
    ops += [gen_query_received_messages] * 1
    return ops


def group_strong():
    set_global_prob(0, 1)
    relation = random.randint(0, 4)
    global MAX_MODIFY_VALUE
    MAX_MODIFY_VALUE = 10
    ops = [gen_add_person] * 12
    ops += [gen_add_relation] * (6 + relation * 3)
    ops += [gen_modify_relation] * (4 + relation * 2)
    ops += [gen_add_group] * 6
    ops += [gen_add_to_group] * 10
    ops += [gen_del_from_group] * 6
    ops += [gen_query_group_value_sum] * 1
    ops += [gen_query_group_age_var] * 1
    return ops


def weak_strong():
    set_global_prob(0, 1)
    global MAX_MODIFY_VALUE
    MAX_MODIFY_VALUE = -100
    relation = random.randint(1, 10)
    ops = [gen_add_person] * 10
    ops += [gen_add_relation] * relation * 5
    ops += [gen_modify_relation] * relation * 2
    ops += [gen_query_circle] * 2
    ops += [gen_query_block_sum] * 1
    ops += [gen_query_triple_sum] * 1
    return ops


def exception_strong():
    set_global_prob(0.2, 0.8)
    ops = [gen_add_person] * 20
    ops += [gen_add_relation] * 30
    ops += [gen_query_value] * 1
    ops += [gen_query_circle] * 1
    ops += [gen_add_group] * 5
    ops += [gen_add_to_group] * 5
    ops += [gen_del_from_group] * 5
    ops += [gen_query_group_value_sum] * 1
    ops += [gen_query_group_age_var] * 1
    ops += [gen_modify_relation] * 5
    ops += [gen_query_best_acquaintance] * 1
    ops += [gen_add_message] * 5
    ops += [gen_send_message] * 5
    ops += [gen_query_social_value] * 1
    ops += [gen_query_received_messages] * 1
    return ops


def inst_normal():
    global cnt, ops
    if cnt % CHANGE_FREQ == 0:
        ops = get_ops()
    cnt += 1
    inst = [gen_add_person() for _ in range(min_ap)]
    inst += [gen_add_group() for _ in range(min_ag)]
    inst += [gen_add_relation() for _ in range(min_ar)]
    inst += [op() for op in random.choices(ops, k=LEN-min_ap-min_ag-min_ar)]

    return inst


def qcs_time_critical():
    ap = random.randint(int(math.sqrt(LEN)), LEN//2)
    qcs = random.randint(LEN//10, LEN//4)
    ar = LEN - ap - qcs
    inst = [gen_add_person() for _ in range(ap)]
    inst += [gen_add_relation() for _ in range(ar)]
    inst += [gen_query_couple_sum()] * qcs
    return inst


get_inst = inst_normal
get_ops = op_normal
min_ar = min(LEN // 10, 10)
min_ap = min(LEN // 10, 10)
min_ag = 1
TYPE = SETTING['type']
if TYPE == 'qcs_time_critical':
    print('qcs_time_critical')
    get_inst = qcs_time_critical
elif TYPE == 'ba' or TYPE in SETTING['ba']:
    print('ba_strong')
    get_ops = ba_strong
elif TYPE == 'message' or TYPE in SETTING['message']:
    print('message_strong')
    get_ops = message_strong
elif TYPE == 'group' or TYPE in SETTING['group']:
    print('group_strong')
    get_ops = group_strong
elif TYPE == 'hw9' or TYPE in SETTING['Rank_C_Congratulations']:
    print('weak_strong')
    get_ops = weak_strong
elif TYPE == 'exception' or TYPE in SETTING['exception']:
    print('exception_strong')
    get_ops = exception_strong
else:
    print(TYPE)
    get_ops = op_normal
ops = get_ops()


def gen():
    person_id.clear()
    group_id.clear()
    message_id.clear()
    return '\n'.join(get_inst())


if __name__ == '__main__':
    print(gen(15))
