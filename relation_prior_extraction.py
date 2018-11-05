import sys
sys.path.append('./FactorizableNet')
import json
import math
import pickle
import numpy as np
import yaml
import lib.datasets as datasets
import lib.utils.general_utils as utils
from settings import parse_args
from SGGenModel import VG_DR_NET_OBJ_IGNORES, VG_DR_NET_PRED_IGNORES, VG_MSDN_OBJ_IGNORES, VG_MSDN_PRED_IGNORES


def distance(o_x, o_y, s_x, s_y):
    return math.sqrt((o_x - s_x) ** 2 + (o_y - s_y) ** 2)

def update_normal(prev_mean, prev_var, prev_num, new_val):
    total = prev_mean * prev_num + new_val
    new_mean = total / (prev_num + 1)
    prev_square_mean = prev_var + prev_mean ** 2
    new_square_mean = (prev_square_mean * prev_num + new_val ** 2) / (prev_num + 1)
    new_var = new_square_mean - new_mean ** 2
    return new_mean, new_var

def save_obj(obj, filename):
    with open(filename + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(filename):
    with open(filename + '.pkl', 'rb') as f:
        return pickle.load(f)


if __name__=="__main__":

    args = parse_args()
    # Set options
    options = {
        'data': {
            'dataset_option': args.dataset_option,
            'batch_size': args.batch_size,
        },
    }
    with open(args.path_opt, 'r') as handle:
        options_yaml = yaml.load(handle)
    options = utils.update_values(options, options_yaml)
    with open(options['data']['opts'], 'r') as f:
        data_opts = yaml.load(f)
        options['data']['dataset_version'] = data_opts.get('dataset_version', None)
        options['opts'] = data_opts
    print("Loading training set and testing set..."),
    test_set = getattr(datasets, options['data']['dataset'])(data_opts, 'test',
                                                             dataset_option='normal',
                                                             batch_size=1,
                                                             use_region=False)
    print("Done")


    '''0. Choose OBJECTS & PREDICTES to be extracted'''
    relevant_classes = sorted([u'field', u'zebra', u'sky', u'track', u'train', u'window', u'pole', u'windshield', u'background', u'tree', u'door', u'sheep', u'paint', u'grass', u'baby', u'ear', u'leg', u'eye', u'tail', u'head', u'nose', u'skateboarder', u'arm', u'foot', u'skateboard', u'wheel', u'hand', u'ramp', u'man', u'jeans', u'shirt', u'sneaker', u'writing', u'hydrant', u'cap', u'chain', u'sidewalk', u'curb', u'road', u'line', u'bush', u'sign', u'people', u'car', u'edge', u'bus', u'tire', u'lady', u'letter', u'leaf', u'boy', u'pocket', u'backpack', u'bottle', u'suitcase', u'word', u'ground', u'handle', u'strap', u'jacket', u'motorcycle', u'bicycle', u'truck', u'cloud', u'kite', u'pants', u'beach', u'woman', u'rock', u'dress', u'dog', u'building', u'frisbee', u'shoe', u'plant', u'pot', u'hair', u'face', u'shorts', u'stripe', u'bench', u'flower', u'cat', u'post', u'container', u'house', u'ceiling', u'seat', u'back', u'graffiti', u'paper', u'hat', u'tennisracket', u'tennisplayer', u'wall', u'logo', u'girl', u'clock', u'brick', u'white', u'elephant', u'mirror', u'bird', u'glove', u'oven', u'area', u'sticker', u'flag', u'surfboard', u'wetsuit', u'shadow', u'sleeve', u'tenniscourt', u'surface', u'finger', u'string', u'plane', u'wing', u'umbrella', u'snow', u'sunglasses', u'boot', u'coat', u'skipole', u'ski', u'skier', u'black', u'player', u'sock', u'racket', u'wrist', u'band', u'ball', u'light', u'shelf', u'stand', u'vase', u'horse', u'number', u'rug', u'goggles', u'snowboard', u'computer', u'screen', u'button', u'glass', u'bracelet', u'cellphone', u'mountain', u'phone', u'hill', u'fence', u'stone', u'cow', u'tag', u'bear', u'table', u'water', u'ocean', u'trashcan', u'circle', u'river', u'railing', u'design', u'bowl', u'food', u'spoon', u'tablecloth', u'plate', u'bread', u'tomato', u'kid', u'sand', u'dirt', u'mouth', u'hole', u'air', u'distance', u'board', u'feet', u'suit', u'wave', u'guy', u'reflection', u'bathroom', u'toilet', u'sink', u'faucet', u'floor', u'toiletpaper', u'towel', u'sandwich', u'knife', u'bolt', u'boat', u'engine', u'trafficlight', u'wine', u'cup', u'stem', u'base', u'top', u'bottom', u'sofa', u'counter', u'photo', u'frame', u'side', u'paw', u'branch', u'fur', u'forest', u'wire', u'headlight', u'rail', u'front', u'green', u'helmet', u'whiskers', u'pen', u'neck', u'net', u'necklace', u'duck', u'sweater', u'chair', u'horn', u'giraffe', u'spot', u'mane', u'airplane', u'beard', u'speaker', u'sun', u'shore', u'pillar', u'tower', u'jet', u'gravel', u'sauce', u'fork', u'tray', u'awning', u'tent', u'bun', u'teeth', u'camera', u'tile', u'lid', u'kitchen', u'curtain', u'drawer', u'knob', u'box', u'outlet', u'remote', u'couch', u'tie', u'book', u'ring', u'toothbrush', u'balcony', u'stairs', u'doorway', u'stopsign', u'bed', u'pillow', u'corner', u'trim', u'vegetable', u'orange', u'broccoli', u'rope', u'streetlight', u'name', u'pitcher', u'uniform', u'body', u'mouse', u'keyboard', u'desk', u'monitor', u'statue', u'collar', u'candle', u'animal', u'tv', u'donut', u'apple', u'child', u'licenseplate', u'catcher', u'umpire', u'banner', u'bat', u'batter', u'part', u'hotdog', u'object', u'cake', u'bridge', u'patch', u'belt', u'park', u'stick', u'bucket', u'runway', u'lamp', u'tip', u'carpet', u'blanket', u'cover', u'napkin', u'theoutdoors', u'stove', u'pizza', u'cheese', u'crust', u'van', u'beak', u'cord', u'poster', u'purse', u'laptop', u'shoulder', u'dish', u'can', u'pipe', u'key', u'arrow', u'surfer', u'controller', u'blinds', u'bluesky', u'whiteclouds', u'luggage', u'vehicle', u'streetsign', u'pan', u'baseball', u'baseballplayer', u'jersey', u'rack', u'cabinet', u'meat', u'watch', u'refrigerator', u'vest', u'skirt', u'hoof', u'label', u'teddybear', u'fridge', u'snowboarder', u'scarf', u'basket', u'cloth', u'shade', u'blue', u'spectator', u'knee', u'column', u'metal', u'steps', u'firehydrant', u'platform', u'jar', u'fruit', u'hood', u't-shirt', u'cone', u'weeds', u'treetrunk', u'room', u'red', u'television', u'scissors', u'gate', u'tennisball', u'court', u'log', u'star', u'lettuce', u'traincar', u'microwave', u'pepperoni', u'onion', u'chimney', u'concrete', u'mug', u'carrot', u'banana', u'cart', u'wood', u'bar', u'ripples', u'holder', u'pepper', u'tusk'])
    print('Before OBJECT filtering: ' + str(len(relevant_classes)))
    to_exclude = ['1', 'field', '2', 'zebra', '3', 'sky', '4', 'track', '5', 'train', '9', 'background', '12', 'sheep', '14', 'grass', '15', 'baby', '16', 'ear', '17', 'leg', '18', 'eye', '19', 'tail', '20', 'head', '21', 'nose', '22', 'skateboarder', '23', 'arm', '24', 'foot', '25', 'skateboard', '27', 'hand', '29', 'man', '34', 'hydrant', '37', 'sidewalk', '38', 'curb', '39', 'road', '43', 'people', '44', 'car', '46', 'bus', '47', 'tire', '48', 'lady', '49', 'letter', '50', 'leaf', '51', 'boy', '64', 'cloud', '65', 'kite', '66', 'pants', '67', 'beach', '68', 'woman', '71', 'dog', '72', 'building', '73', 'frisbee', '77', 'hair', '78', 'face', '79', 'shorts', '83', 'cat', '94', 'tennisplayer', '97', 'girl', '101', 'elephant', '103', 'bird', '111', 'shadow', '112', 'sleeve', '113', 'tenniscourt', '114', 'surface', '115', 'finger', '120', 'snow', '121', 'sunglasses', '126', 'skier', '128', 'player', '131', 'wrist', '138', 'horse', '151', 'hill', '152', 'fence', '154', 'cow', '156', 'bear', '162', 'river', '163', 'railing', '172', 'kid', '175', 'mouth', '177', 'air', '178', 'distance', '180', 'feet', '182', 'wave', '183', 'guy', '184', 'reflection', '200', 'stem', '209', 'paw', '210', 'branch', '212', 'forest', '215', 'rail', '219', 'whiskers', '221', 'neck', '223', 'necklace', '224', 'duck', '228', 'giraffe', '230', 'mane', '232', 'beard', '234', 'sun', '235', 'shore', '237', 'tower', '239', 'gravel', '243', 'awning', '244', 'tent', '246', 'teeth', '276', 'pitcher', '277', 'uniform', '278', 'body', '286', 'animal', '290', 'child', '291', 'licenseplate', '292', 'catcher', '293', 'umpire', '296', 'batter', '301', 'bridge', '304', 'park', '307', 'runway', '314', 'theoutdoors', '319', 'van', '320', 'beak', '325', 'shoulder', '331', 'surfer', '334', 'bluesky', '335', 'whiteclouds', '337', 'vehicle', '340', 'baseball', '341', 'baseballplayer', '350', 'hoof', '354', 'snowboarder', '358', 'shade', '360', 'spectator', '361', 'knee', '366', 'platform', '372', 'weeds', '373', 'treetrunk', '396', 'ripples', '399', 'tusk']
    for ex in to_exclude:
        if ex in relevant_classes:
            relevant_classes.remove(ex)
    obj_ind2key = {idx: item for idx, item in enumerate(relevant_classes)}
    obj_key2ind = {item: idx for idx, item in enumerate(relevant_classes)}
    save_obj(obj_ind2key,filename='object_prior_ind2key')
    save_obj(obj_key2ind,filename='object_prior_key2ind')
    print('After OBJECT filtering: ' + str(len(relevant_classes)))

    print('Before PREDICATE filtering: ' + str(len(test_set.predicate_classes)))
    pred_cls = range(len(test_set.predicate_classes))
    pred_cls = [p for p in pred_cls if not p in VG_DR_NET_PRED_IGNORES]
    pred_cls = [test_set.predicate_classes[x] for x in pred_cls]
    pred_ind2key = {idx: item for idx, item in enumerate(pred_cls)}
    pred_key2ind = {item: idx for idx, item in enumerate(pred_cls)}
    save_obj(pred_ind2key,filename='pred_prior_ind2key.pkl')
    save_obj(pred_key2ind,filename='pred_prior_key2ind.pkl')
    print('After PREDICATE filtering: ' + str(len(pred_cls)))



    '''1. start constructing relation prior'''
    extract_statistics = True
    if extract_statistics:
        file = open('relationships.json').read()
        data = json.loads(file)
        print("Reading JSON completed!!")

        statistics = {}
        predicates = {}
        i = 0
        for datum in data:
            i += 1
            if i % 1000 == 0:
                print(str(i) + "th point processing")

            relations = datum['relationships']

            for rel in relations:
                pred, obj, sub = rel['predicate'], rel['object']['name'], rel['subject']['name']
                pred = pred.lower()
                obj_x, obj_y, sub_x, sub_y = rel['object']['x'], rel['object']['y'], rel['subject']['x'], rel['subject']['y']
                if obj in relevant_classes and sub in relevant_classes and pred in pred_cls:
                    curr_dist = distance(obj_x, obj_y, sub_x, sub_y)
                    if (sub, obj) in statistics:
                        if pred in statistics[(sub, obj)]:
                            statistics[(sub, obj)][pred]['count'] += 1
                            statistics[(sub, obj)][pred]['dist'].append(curr_dist)
                        else:
                            statistics[(sub, obj)][pred] = {'count': 1, 'dist': [curr_dist]}
                    else:
                        statistics[(sub, obj)] = {}
                        statistics[(sub, obj)][pred] = {'count': 1, 'dist': [curr_dist]}
                if pred in predicates:
                    predicates[pred] += 1
                else:
                    predicates[pred] = 1
        save_obj(statistics, "relation_prior")




    '''2. processing relation prior'''
    statistics = load_obj("relation_prior")
    keys = list(statistics)
    for item in keys:
        for predicate in statistics[item]:
            statistics[item][predicate]['mean'] = np.mean(statistics[item][predicate]['dist'])
            statistics[item][predicate]['var'] = np.var(statistics[item][predicate]['dist'])
            del statistics[item][predicate]['dist']
    save_obj(statistics, 'relation_prior_prob')
