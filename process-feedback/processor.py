#!/usr/bin/env python3


import sys
import json
import pickle
import os
import re
import statistics
from anytree import NodeMixin, RenderTree, PreOrderIter

from text_categorizer import categorize_all_texts, update_keywords
from llm_client import analyze_with_gemini


class FeedbackAverage():

    def __init__(self, name):
        self.collection = {
            'eval_overall': {
                'title': 'Evaluarea dumneavoastră generală cu privire la această disciplină este pozitivă?',
                'items': []
                },
            'expected_grade': {
                'title': 'Care este nota pe care vă așteptați să o obțineți la această disciplină?',
                'items': []
                },
            'load': {
                'title': 'Încărcarea generală la această disciplină este mai mică decât cea a altor discipline care oferă același număr de credite?',
                'items': []
                },
            'equipment': {
                'title': 'Dotarea (locație / echipamente hardware și software / suport digital) este adecvată activităților acestei discipline?',
                'items': []
                },
            'part': {
                'title': 'Numărul aproximativ de activități la care ați participat (curs + aplicații):',
                'items': []
                },
            'prof_know': {
                'title': 'Cadrul didactic stăpânește bine domeniul de studiu?',
                'items': []
                },
            'prof_teach': {
                'title': 'Metoda de expunere a fost potrivită?',
                'items': []
                },
            'prof_interact': {
                'title': 'Cursul a stimulat discuțiile și cadrul didactic a răspuns clar întrebărilor studenților?',
                'items': []
                },
            'prof_behave': {
                'title': 'Comportamentul cadrului didactic față de studenți a fost adecvat?',
                'items': []
                },
            'lecture_doc': {
                'title': 'Materialele didactice puse la dispoziție sunt suficiente pentru înțelegerea cursului?',
                'items': []
                },
            'assist_know': {
                'title': 'Cadrul didactic stăpânește bine domeniul de studiu?',
                'items': []
                },
            'assist_teach': {
                'title': 'Cadrul didactic a sprijinit activitatea individuală a studenților?',
                'items': []
                },
            'assist_interact': {
                'title': 'Aplicațile au stimulat discuțiile și cadrul didactic a răspuns clar întrebărilor studenților?',
                'items': []
                },
            'assist_behave': {
                'title': 'Comportamentul cadrului didactic față de studenți a fost adecvat?',
                'items': []
                },
            'lab_doc': {
                'title': 'Materialele didactice puse la dispoziție sunt suficiente pentru înțelegerea aplicațiilor?',
                'items': []
                },
            'assign_time': {
                'title': 'Estimați numărul mediu de ore pe săptămână dedicate rezolvării temelor',
                'items': []
                },
            'assign_diff': {
                'title': 'Numărul și dificultatea temelor au fost adecvate?',
                'items': []
                },
            'assign_useful': {
                'title': 'Temele/proiectele/activitățile practice au ajutat la înțelegerea materiei?',
                'items': []
                },
            }
        self.num = 0
        self.overall_prof = {
                'value': 0.0,
                'stdev': 0.0
                }
        self.overall_assist = {
                'value': 0.0,
                'stdev': 0.0
                }
        self.name = name
        self.result = {}

    def add_response(self, response):
        for k, v in self.collection.items():
            if response[k]:
                v['items'].append(response[k])
        self.num += 1

    def add_response_list(self, responses):
        for r in responses:
            self.add_response(r)

    def compute(self):
        try:
            self.overall_prof['value'] = (statistics.mean(self.collection['prof_know']['items']) +
                    statistics.mean(self.collection['prof_teach']['items']) +
                    statistics.mean(self.collection['prof_interact']['items']) +
                    statistics.mean(self.collection['prof_behave']['items'])) / 4
        except statistics.StatisticsError:
            self.overall_prof['value'] = 0.0

        try:
            self.overall_assist['value'] = (statistics.mean(self.collection['assist_know']['items']) +
                    statistics.mean(self.collection['assist_teach']['items']) +
                    statistics.mean(self.collection['assist_interact']['items']) +
                    statistics.mean(self.collection['assist_behave']['items'])) / 4
        except statistics.StatisticsError:
            self.overall_assist['value'] = 0.0

        try:
            self.overall_prof['stdev'] = (statistics.stdev(self.collection['prof_know']['items']) +
                    statistics.stdev(self.collection['prof_teach']['items']) +
                    statistics.stdev(self.collection['prof_interact']['items']) +
                    statistics.stdev(self.collection['prof_behave']['items'])) / 4
        except statistics.StatisticsError:
            self.overall_assist['stdev'] = 0.0

        try:
            self.overall_assist['stdev'] = (statistics.stdev(self.collection['assist_know']['items']) +
                    statistics.stdev(self.collection['assist_teach']['items']) +
                    statistics.stdev(self.collection['assist_interact']['items']) +
                    statistics.stdev(self.collection['assist_behave']['items'])) / 4
        except statistics.StatisticsError:
            self.overall_assist['stdev'] = 0.0

        res = {}
        res['name'] = {
                'title': 'Curs / Persoană',
                'value': self.name
                }
        res['num'] = {
                'title': 'Număr feedbackuri',
                'value': self.num
                }
        res['num_students'] = {
                'title': 'Număr de studenți',
                'value': None,
                }
        res['percentage'] = {
                'title': 'Procentaj de feedback primit',
                'value': None
                }
        res['overall_prof'] = {
                'title': 'Evaluare agregată titular curs',
                'value': self.overall_prof['value'],
                'stdev': self.overall_prof['stdev']
                }
        res['overall_assist'] = {
                'title': 'Evaluare agregată titular laborator',
                'value': self.overall_assist['value'],
                'stdev': self.overall_assist['stdev']
                }
        for k, v in self.collection.items():
            try:
                m = statistics.mean(v['items'])
            except statistics.StatisticsError:
                m = 0

            try:
                s = statistics.stdev(v['items'], m)
            except statistics.StatisticsError:
                s = 0

            res[k] = {
                    'title': v['title'],
                    'value': m,
                    'stdev': s
                    }
        self.result = res

    def get_result(self):
        return self.result

    def print(self):
        value = "{:40s}".format(self.name)
        for k, v in self.result.items():
            if v['value']:
                if k == 'num':
                    value += ",{:6d}".format(v['value'])
                else:
                    value += ",{:6.2f}".format(v['value'])
            else:
                value += ",  None"
        print(value)


class FeedbackContent():

    keys = [
            'course',
            'prof',
            'assist',
            'eval_overall',
            'expected_grade',
            'load',
            'equipment',
            'part',
            'prof_know',
            'prof_teach',
            'prof_interact',
            'prof_behave',
            'lecture_doc',
            'assist_know',
            'assist_teach',
            'assist_interact',
            'assist_behave',
            'lab_doc',
            'assign_time',
            'assign_diff',
            'assign_useful',
            'positive',
            'negative',
            'difficulty',
            'other'
            ]

    feedback_data = {
            'course': {
                'title': 'Disciplina',
                'values': []
                },
            'prof': {
                'title': 'Titularul cursului',
                'values': []
                },
            'assist': {
                'title': 'Titularul laboratorului / seminarului / proiectului',
                'values': []
                },
            'eval_overall': {
                'title': 'Evaluarea dumneavoastră generală cu privire la această disciplină este pozitivă?',
                'values': []
                },
            'expected_grade': {
                'title': 'Care este nota pe care vă așteptați să o obțineți la această disciplină?',
                'values': []
                },
            'load': {
                'title': 'Încărcarea generală la această disciplină este mai mică decât cea a altor discipline care oferă același număr de credite?',
                'values': []
                },
            'equipment': {
                'title': 'Dotarea (locație / echipamente hardware și software / suport digital) este adecvată activităților acestei discipline?',
                'values': []
                },
            'part': {
                'title': 'Numărul aproximativ de activități la care ați participat (curs + aplicații):',
                'values': []
                },
            'prof_know': {
                'title': 'Cadrul didactic stăpânește bine domeniul de studiu?',
                'values': []
                },
            'prof_teach': {
                'title': 'Metoda de expunere a fost potrivită?',
                'values': []
                },
            'prof_interact': {
                'title': 'Cursul a stimulat discuțiile și cadrul didactic a răspuns clar întrebărilor studenților?',
                'values': []
                },
            'prof_behave': {
                'title': 'Comportamentul cadrului didactic față de studenți a fost adecvat?',
                'values': []
                },
            'lecture_doc': {
                'title': 'Materialele didactice puse la dispoziție sunt suficiente pentru înțelegerea cursului?',
                'values': []
                },
            'assist_know': {
                    'title': 'Cadrul didactic stăpânește bine domeniul de studiu?',
                    'values': []
                    },
            'assist_teach': {
                    'title': 'Cadrul didactic a sprijinit activitatea individuală a studenților?',
                    'values': []
                    },
            'assist_interact': {
                    'title': 'Aplicațile au stimulat discuțiile și cadrul didactic a răspuns clar întrebărilor studenților?',
                    'values': []
                    },
            'assist_behave': {
                    'title': 'Comportamentul cadrului didactic față de studenți a fost adecvat?',
                    'values': []
                    },
            'lab_doc': {
                    'title': 'Materialele didactice puse la dispoziție sunt suficiente pentru înțelegerea aplicațiilor?',
                    'values': []
                    },
            'assign_time': {
                    'title': 'Estimați numărul mediu de ore pe săptămână dedicate rezolvării temelor',
                    'values': []
                    },
            'assign_diff': {
                    'title': 'Numărul și dificultatea temelor au fost adecvate?',
                    'values': []
                    },
            'assign_useful': {
                    'title': 'Temele/proiectele/activitățile practice au ajutat la înțelegerea materiei?',
                    'values': []
                    },
            'positive': {
                    'title': 'Care sunt aspectele pozitive ale acestei discipline?',
                    'values': []
                    },
            'negative': {
                    'title': 'Ce considerați că trebuie îmbunătățit la această disciplină?',
                    'values': []
                    },
            'difficulty': {
                    'title': 'După părerea dumneavoastră, dificultatea principală în urmărirea acestei discipline provine din:',
                    'values': []
                    },
            'other': {
                    'title': 'Alte comentarii personale sau sugestii referitoare la activitățile desfășurate la această disciplină:',
                    'values': []
                    }
            }

    def __init__(self, processor):
        self.feedback_list = []

        self.average_overall = {}
        self.average_per_disc = {}
        self.average_per_prof = {}
        self.average_per_assist = {}

        self.processor = processor
        self.result = {
                'overall': {},
                'courses': {},
                'profs': {},
                'assists': {}
            }

    def convert_value(self, key, raw):
        if key == 'eval_overall' or key == 'load' or key == 'equipment' \
            or key == 'prof_know' or key == 'prof_teach' or key == 'prof_interact' \
            or key == 'prof_behave'  or key == 'lecture_doc' or key == 'assist_know' \
            or key == 'assist_teach' or key == 'assist_interact' or key == 'assist_behave' \
            or key == 'lab_doc' or key == 'assign_diff' or key == 'assign_useful':
                try:
                    value = int(raw)
                except ValueError:
                    value = None
                if value:
                    value = 6 - value
                return value

        if key == 'expected_grade' or key == 'part' or key == 'assign_time':
            try:
                value = int(raw)
            except ValueError:
                value = None
            return value

        return raw

    def select_responses_by_key(self, key, value):
        select_list = []
        for r in self.feedback_list:
            if r[key] == value:
                select_list.append(r)
        return select_list

    def compute_average_overall(self):
        fa = FeedbackAverage("Medie")
        fa.add_response_list(self.feedback_list)
        fa.compute()
        self.result['overall'] = fa.get_result()

    def get_courses(self):
        return sorted(set([r['course'] for r in self.feedback_list]))

    def get_profs(self):
        return sorted(set([r['prof'] for r in self.feedback_list]))

    def get_assists(self):
        return sorted(set([r['assist'] for r in self.feedback_list]))

    def is_prof_for_course(self, prof, course):
        for item in self.select_responses_by_key('prof', prof['fullname']):
            if item['course'] == course.shortname:
                return True
        return False

    def compute_average_per_course(self):
        for item in self.get_courses():
            fa = FeedbackAverage(item)
            fa.add_response_list(self.select_responses_by_key('course', item))
            fa.compute()
            self.result['courses'][item] = fa.get_result()

    def compute_average_per_prof(self):
        for item in self.get_profs():
            fa = FeedbackAverage(item)
            fa.add_response_list(self.select_responses_by_key('prof', item))
            fa.compute()
            self.result['profs'][item] = fa.get_result()

    def compute_average_per_assist(self):
        for item in self.get_assists():
            fa = FeedbackAverage(item)
            fa.add_response_list(self.select_responses_by_key('assist', item))
            fa.compute()
            self.result['assists'][item] = fa.get_result()

    def compute_text_categories(self):
        """Categorize textual feedback from 'other' field.

        Extracts free-text responses, runs local keyword matching,
        falls back to Gemini for uncategorized texts, and updates
        the keywords DB with new suggestions.
        """
        # Get all 'other' field texts and filter out empty ones
        raw_texts = self.feedback_data["other"]["values"]
        texts = [t for t in raw_texts if t and str(t).strip()]

        if not texts:
            # No texts to categorize
            self.result["text_categories"] = {
                "categorized": {},
                "uncategorized": [],
                "stats": {}
            }
            return

        # Step 1: Run local keyword-based categorization
        local_result = categorize_all_texts(texts)

        # Step 2: If there are uncategorized texts, try Gemini
        if local_result["uncategorized"]:
            gemini_result = analyze_with_gemini(local_result["uncategorized"])

            if gemini_result is not None:
                # Merge Gemini results into local results
                for text, categories in gemini_result["results"].items():
                    local_result["categorized"][text] = categories
                    # Update stats with Gemini categories
                    for cat in categories:
                        if cat in local_result["stats"]:
                            local_result["stats"][cat] += 1

                # Remove texts that Gemini categorized from uncategorized
                gemini_texts = set(gemini_result["results"].keys())
                local_result["uncategorized"] = [
                    t for t in local_result["uncategorized"]
                    if t not in gemini_texts
                ]

                # Step 3: Update keywords DB with Gemini suggestions
                if gemini_result["new_keywords"]:
                    update_keywords(gemini_result["new_keywords"])

        # Save the combined results
        self.result["text_categories"] = local_result

    def compute_averages(self):
        self.compute_average_overall()
        self.compute_average_per_course()
        self.compute_average_per_prof()
        self.compute_average_per_assist()
        self.compute_text_categories()

    def key_value_for_response(self, index, r):
        k = self.keys[index]
        v = self.convert_value(k, r['rawval'])
        return k, v

    def add_json(self, json_contents):
        data = json.loads(json_contents)
        for attempt in data['anonattempts']:
            r_dict = {}
            for i, r in enumerate(attempt['responses']):
                k, v = self.key_value_for_response(i, r)
                self.feedback_data[k]['values'].append(v)
                r_dict[k] = v
            self.feedback_list.append(r_dict)

    def get_result(self):
        return self.result

    def print(self):
        print(self.result)

    def print_raw(self):
        print(self.feedback_data)
        print(self.feedback_list)

    def print_selection_items(self):
        print("courses:", self.get_courses())
        print("profs:", self.get_profs())
        print("assists:", self.get_assists())


class Course():

    def __init__(self, course_id, processor):
        self.id = course_id
        self.processor = processor
        self.shortname = next((c['shortname'] for c in self.processor.courses if c['id'] == course_id))
        self.num_students = self.processor.num_students4course(course_id)
        self.feedback_id = self.processor.feedback4course(course_id)
        self.profs = self.processor.profs4course(course_id=course_id)
        self.assists = self.processor.assists4course(course_id=course_id)

    def has_feedback(self):
        return self.feedback_id != None


class Group():

    def __init__(self, processor, blacklist=None):
        self.courses = []
        if blacklist:
            self.blacklist = re.compile(blacklist)
        else:
            # If no blacklist, compile regex that matches nothing.
            self.blacklist = re.compile('.^')
        self.blacklisted_courses = []
        self.rejected_courses = []
        self.processor = processor
        self.students4prof = {}
        self.students4course = {}
        self.result = {}
        self.processor = processor
        self.feedback = FeedbackContent(self.processor)

    def add_course(self, course_id):
        c = Course(course_id, self.processor)
        if self.blacklist.match(c.shortname):
            print("blacklisting {} ({})".format(c.shortname, c.id))
            self.blacklisted_courses.append(c)
            return
        if c.has_feedback():
            try:
                self.feedback.add_json(self.processor.get_feedback_file_contents(c.feedback_id))
            except:
                print("Unusable feedback for course {}".format(c.shortname))
                self.rejected_courses.append(c)
                return
        self.courses.append(c)
        self.students4course[c.shortname] = c.num_students
        for p in c.profs:
            if self.feedback.is_prof_for_course(p, c):
                if p['fullname'] in self.students4prof.keys():
                    self.students4prof[p['fullname']] += c.num_students
                else:
                    self.students4prof[p['fullname']] = c.num_students

    def add_category(self, category_id):
        for c in self.processor.courses4category(category_id):
            self.add_course(c)

    def process(self):
        self.feedback.compute_averages()
        self.result = self.feedback.get_result()
        for k in self.result['courses'].keys():
            self.result['courses'][k]['num_students']['value'] = self.students4course[k]
            if self.result['courses'][k]['num_students']['value'] != 0:
                self.result['courses'][k]['percentage']['value'] = float(self.result['courses'][k]['num']['value']) / self.result['courses'][k]['num_students']['value'] * 100
            else:
                self.result['courses'][k]['percentage']['value'] = 0.0
        for k in self.result['profs'].keys():
            if k in self.students4prof.keys():
                self.result['profs'][k]['num_students']['value'] = self.students4prof[k]
                if self.result['profs'][k]['num_students']['value'] != 0:
                    self.result['profs'][k]['percentage']['value'] = float(self.result['profs'][k]['num']['value']) / self.result['profs'][k]['num_students']['value'] * 100
                else:
                    self.result['profs'][k]['percentage']['value'] = 0.0
            else:
                self.result['profs'][k]['num_students']['value'] = 0
                self.result['profs'][k]['percentage']['value'] = 0.0
        self.result['overall']['num_students']['value'] = sum([self.result['courses'][k]['num_students']['value'] for k in self.result['courses'].keys()])
        if self.result['overall']['num_students']['value'] != 0:
            self.result['overall']['percentage']['value'] = float(self.result['overall']['num']['value']) / self.result['overall']['num_students']['value'] * 100
        else:
            self.result['overall']['percentage']['value'] = 0.0
        self.result['courses_list'] = [c.shortname for c in self.courses]
        self.result['blacklisted'] = [c.shortname for c in self.blacklisted_courses]
        self.result['rejected'] = [c.shortname for c in self.rejected_courses]

    def get_result(self):
        return self.result

    def print_line(self, data):
        value = "{:40s}".format(data['name']['value'])
        for k, v in data.items():
            if v['value']:
                if k == 'name':
                    continue
                if k == 'num':
                    value += ",{:6d}".format(v['value'])
                if k == 'percentage':
                    value += ",{:5.2f}%".format(v['value'])
                else:
                    value += ",{:6.2f}".format(v['value'])
            else:
                value += ",  None"
        print(value)

    def print(self):
        self.print_line(self.result['overall'])
        for k, v in self.result['courses'].items():
            self.print_line(v)
        for k, v in self.result['profs'].items():
            self.print_line(v)
        for k, v in self.result['assists'].items():
            self.print_line(v)


class Processor():

    def __init__(self, courses_file, categories_file, courses4categories_file, feedbacks_file, feedbacks_dir, users_dir):
        self.courses = pickle.load(open(courses_file, 'rb'))
        self.categories = pickle.load(open(categories_file, 'rb'))
        self.courses4categories = pickle.load(open(courses4categories_file, 'rb'))
        self.feedbacks = pickle.load(open(feedbacks_file, 'rb'))
        self.feedbacks_dir = feedbacks_dir
        self.users_dir = users_dir

    def get_feedback_file_contents(self, feedback_id):
        """Get contents of feedback file by feedback id.
        """
        return(open(os.path.join(self.feedbacks_dir, "{}.json".format(feedback_id))).read())

    def is_course_feedback(self, feedback_id):
        """Validate feedback format.
        """
        with open(os.path.join(self.feedbacks_dir, "{}.json".format(feedback_id))) as f:
            data = json.load(f)
            if 'anonattempts' in data.keys():
                if len(data['anonattemtps']) == 0:
                    return True
                if len(data['anonattempts'][0]['responses']) == 25:
                    return True
        return False

    def num_entries_in_feedback(self, feedback_id):
        """Get number of entries in a feedback.
        """
        with open(os.path.join(self.feedbacks_dir, "{}.json".format(feedback_id))) as f:
            data = json.load(f)
            if 'anonattempts' in data.keys():
                if len(data['anonattempts']) == 0:
                    return 0
                if len(data['anonattempts'][0]['responses']) == 25:
                    return len(data['anonattempts'])
        return -1

    def feedback4course(self, course_id):
        """Return valid feedback id for a given course.
        """
        shortname = next((c['shortname'] for c in self.courses if c['id'] == course_id))
        feeds = [feed for feed in self.feedbacks if feed['course'] == course_id]
        ret_f_id = None
        if len(feeds) == 0:
            print("No feedback for course ({}, {})".format(course_id, shortname))
        elif len(feeds) > 1:
            print("Multiple feedbacks for course ({}, {})".format(course_id, shortname))
            num_feeds = -1
            for f in feeds:
                if self.num_entries_in_feedback(f['id']) > num_feeds:
                    ret_f_id = f['id']
                    num_feeds = self.num_entries_in_feedback(f['id'])
        else:
            ret_f_id = feeds[0]['id']

        return ret_f_id

    def courses4category(self, category_id):
        """Return valid course ids for a given category.
        """
        try:
            return self.courses4categories[category_id]
        except:
            return []

    def feedbacks4category(self, category_id):
        """Return feedback ids for a given category.
        """
        for course_id in self.courses4category(category_id):
            feedback_id = self.feedback4course(course_id)
            shortname = next((c['shortname'] for c in self.courses if c['id'] == course_id))
            if feedback_id == None:
                print("{} ({}): {} (None)".format(course_id, shortname, feedback_id))
            else:
                print("{} ({}): {} ({})".format(course_id, shortname, feedback_id, self.num_entries_in_feedback(feedback_id)))

    def users4course_by_role(self, role, course_id=None, course_name=None):
        """Return students enrolled in a given course.
        """
        students = []
        if course_name != None:
            course_id = next((c['id'] for c in self.courses if c['shortname'] == course_name))
        if course_id != None:
            with open(os.path.join(self.users_dir, "{}.json".format(course_id))) as f:
                data = json.load(f)
                for s in data:
                    if [r for r in s['roles'] if r['shortname'] == role]:
                        students.append(s)
        return students

    def students4course(self, course_id=None, course_name=None):
        """Return students enrolled in a given course.
        """
        try:
            return self.users4course_by_role('student', course_id, course_name)
        except:
            return []

    def profs4course(self, course_id=None, course_name=None):
        """Return teachers enrolled in a given course.
        """
        try:
            return self.users4course_by_role('editingteacher', course_id, course_name)
        except:
            return []

    def assists4course(self, course_id=None, course_name=None):
        """Return assistants enrolled in a given course.
        """
        try:
            return self.users4course_by_role('asistent', course_id, course_name)
        except:
            return []

    def num_students4course(self, course_id=None, course_name=None):
        """Return numer of students enrolled in a given course.
        """
        return len(self.students4course(course_id, course_name))

    def courses4prof(self, prof=None):
        """Return courses for a given professor.
        """
        courses = []
        for c in self.courses:
            if prof['fullname'] in self.profs4course(course_id=c['id']):
                courses.append(c)
        return courses

    def students4prof(self, prof=None):
        """Return students for a professor.
        """
        students = []
        for c in self.courses4prof(prof):
            students.extend(self.students4course(course_id=c['id']))
        return students

    def num_students4prof(self, prof=None):
        """Return numer of students for a professor.
        """
        num_students = 0
        for c in self.courses4prof(prof):
            num_students += self.num_students4course(course_id=c['id'])
        return num_students

    def print_category(self, category_id):
        category_name = next((c['name'] for c in self.categories if c['id'] == category_id))
        print(" === {} ({})".format(category_id, category_name))
        for course_id in self.courses4category(category_id):
            shortname = next((c['shortname'] for c in self.courses if c['id'] == course_id))
            feedback_id = self.feedback4course(course_id)
            if feedback_id != None:
                num_feedbacks = self.num_entries_in_feedback(feedback_id)
            else:
                num_feedbacks = -1
            num_students = self.num_students4course(course_id)
            if num_students != 0 and num_feedbacks != -1:
                percent = float(num_feedbacks) / num_students * 100.0
            else:
                percent = float(0)
            print("course: {} ({}), students: {}, feedback: {} ({}) - {:.2f}%".format(course_id, shortname, num_students, feedback_id, num_feedbacks, percent))

    def construct_group_for_category_id(self, category_id):
        #g = Group(self, '^([0-9]+-[^-]+-(M-A[1-2]-S[1-2]-(CSP|[cC]ercet)|[LM]-A[1-4]-S2)|[^0-9])')
        g = Group(self, '^([0-9]+-[^-]+-(M-A[1-2]-S[1-2]-(CSP|[cC]ercet))|[^0-9])')
        g.add_category(category_id)
        g.process()
        return g

    def construct_class_groups_for_category_id(self, category_id):
        #g = Group(self, '^([0-9]+-[^-]+-(M-A[1-2]-S[1-2]-(CSP|[cC]ercet)|[LM]-A[1-4]-S2)|[^0-9])')
        g = Group(self, '^([0-9]+-[^-]+-(M-A[1-2]-S[1-2]-(CSP|[cC]ercet))|[^0-9])')
        g.add_category(category_id)
        g.process()

        #g_bachelor = Group(self, '^([0-9]+-[^-]+-(M-|[LM]-A[1-4]-S2)|[^0-9])')
        g_bachelor = Group(self, '^([0-9]+-[^-]+-(M-)|[^0-9])')
        g_bachelor.add_category(category_id)
        g_bachelor.process()

        #g_master = Group(self, '^([0-9]+-[^-]+-(M-A[1-2]-S[1-2]-(CSP|[cC]ercet)|[LM]-A[1-4]-S2|L-)|[^0-9])')
        g_master = Group(self, '^([0-9]+-[^-]+-(M-A[1-2]-S[1-2]-(CSP|[cC]ercet)|L-)|[^0-9])')
        g_master.add_category(category_id)
        g_master.process()

        return {'all': g,
                'bachelor': g_bachelor,
                'master': g_master
                }

    def construct_group_for_course_id(self, course_id):
        g = Group(self, '^([0-9]+-[^-]+-(M-A[1-2]-S[1-2]-(CSP|[cC]ercet))|[^0-9])')
        g.add_course(course_id)
        g.process()
        return g
