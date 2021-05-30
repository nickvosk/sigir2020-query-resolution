import argparse
import json
import os


def _is_first_turn(qid, dataset_name):
    return (dataset_name == 'quac' and qid.endswith('q#0')) \
           or (dataset_name.startswith('cast') and qid.endswith('_1'))


def generate_single_model_query_file(dataset_name, qrels, model_output_file, qid2curquestion, output_file):

    model_output_dct = json.load(open(model_output_file))

    id2model_output = dict()
    for qid, x_input, y_pred in zip(model_output_dct['ids'], model_output_dct['x_input'],
                                    model_output_dct['y_pred']):
        id2model_output[qid] = {'x_input': x_input,
                                'y_pred': y_pred}
    num_queries = 0

    with open(output_file, 'w') as fw:
        for qid in qrels:

            num_queries += 1
            cur_question = qid2curquestion[qid]
            cur_question_expansion = str(cur_question)

            if _is_first_turn(qid, dataset_name):
                predicted_tokens = None
            else:
                x_input = id2model_output[qid]['x_input']
                y_pred = id2model_output[qid]['y_pred']
                predicted_tokens = set([w for w, l in zip(x_input, y_pred) if l == 'REL'])

            if predicted_tokens:
                cur_question_expansion += ' ' + ' '.join(predicted_tokens)
            fw.write('{}\t{}\n'.format(qid, cur_question_expansion))

    print('Written {} queries.'.format(num_queries))


def read_qid2curquestion(input_filename):

    qid2curquestion = dict()
    with open(input_filename) as fin:
        for line in fin:
            qid, curquestion = line.strip().split('\t')
            qid2curquestion[qid] = curquestion
    return qid2curquestion


def _get_qrel_file(dataset_name, split, data_dir='/ivi/ilps/projects/Trec_CAST_2019/'):
    if dataset_name == 'quac':
        path = os.path.join(data_dir,
                            'quac_sigir_data/qrel_files/quac_v0.2_qrel_{}.json'.format(split))

    elif dataset_name == 'cast':
        path = os.path.join(data_dir,
                            'cast_sigir_data/qrel_files/cast_v1.0_qrel_{}.json'.format(split))
    else:
        raise ValueError
    return path


def generate_query_file(raw_query_filename, model_output_file, output_file, dataset_name):
    qid2curquestion = read_qid2curquestion(raw_query_filename)

    # print(len(qid2curquestion))

    qrels = list(qid2curquestion.keys())
    # print(qrels[:5])

    generate_single_model_query_file(dataset_name, qrels, model_output_file, qid2curquestion, output_file)

    print('Done.')

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--model_output_file",
                        type=str,
                        required=True)

    parser.add_argument("--raw_query_file",
                        type=str,
                        required=True)

    parser.add_argument("--dataset_name",
                        default='cast',
                        type=str,
                        required=True)

    parser.add_argument("--output_file",
                        type=str,
                        required=True,
                        )

    args = parser.parse_args()

    generate_query_file(args.raw_query_file,
                        args.model_output_file,
                        args.output_file,
                        args.dataset_name)


if __name__ == '__main__':
    main()
