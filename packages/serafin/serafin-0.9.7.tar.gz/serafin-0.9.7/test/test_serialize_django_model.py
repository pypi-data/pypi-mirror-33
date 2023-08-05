# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# 3rd party imports
# import pytest
# # import pytz
# # from django.db import models as db
# # from factory import fuzzy
# # from factory.django import DjangoModelFactory
#
# # local imports
# # from serafin import serialize
# # enable model serializer           pylint: disable=unused-import
# from serafin.django import serialize_django_model
#
#
# # class SimpleModel(db.Model):
# #     """ A simple model without any relations. """
# #     name = db.CharField(max_length=100)
# #     age = db.IntegerField()
# #     height = db.FloatField()
# #     created_dt = db.DateTimeField(auto_now_add=True)
# #
# #     @property
# #     def days_exists(self):
# #         """ Return the number of days since the model was created. """
# #         diff = datetime.now(pytz.utc) - self.created_dt
# #         return diff.total_seconds() / 86400
# #
# #
# # class SimpleModelFactory(DjangoModelFactory):
# #     """ Easily create SimpleModel instances. """
# #     class Meta:     # pylint: disable=missing-docstring
# #         model = SimpleModel
# #
# #     name = fuzzy.FuzzyText(length=24)
# #     age = fuzzy.FuzzyInteger(10, 40)
# #     height = fuzzy.FuzzyFloat(1.3, 2.3)
# #     created_dt = fuzzy.FuzzyDateTime(datetime(2017, 10, 1, tzinfo=pytz.utc))
# #
# #
# # class Person(db.Model):
# #     """ Fake person model for testing. """
# #     name = db.CharField(max_length=100)
# #     age = db.IntegerField()
# #     height = db.FloatField()
# #     created_dt = db.DateTimeField(auto_now_add=True)
# #
# #     @property
# #     def days_active(self):
# #         """ Days since the person record was created. """
# #         diff = datetime.now(pytz.utc) - self.created_dt
# #         return diff.total_seconds() / 86400
# #
# #
# # class PersonFactory(DjangoModelFactory):
# #     """ Easily create Person instances. """
# #     class Meta:     # pylint: disable=missing-docstring
# #         model = Person
# #
# #     name = fuzzy.FuzzyText(length=24)
# #     age = fuzzy.FuzzyInteger(10, 40)
# #     height = fuzzy.FuzzyFloat(1.3, 2.3)
# #     created_dt = fuzzy.FuzzyDateTime(datetime(2017, 10, 1, tzinfo=pytz.utc))
# #
# #
# # class BlogPost(db.Model):
# #     """ Fake blog post model for testing. """
# #     title = db.CharField(max_length=200)
# #     content = db.TextField()
# #     author = db.ForeignKey('Person', related_name='blog_posts')
# #
# #
# # class BlogPostFactory(DjangoModelFactory):
# #     """ Easily create BlogPost instances. """
# #     class Meta:     # pylint: disable=missing-docstring
# #         model = BlogPost
# #
# #     title = fuzzy.FuzzyText(length=24)
# #     content = fuzzy.FuzzyText(length=400)
# #     author = SubFactory(PersonFactory)
# #
#
# # ########### Tests #############
#
#
# @pytest.mark.skip()
# @pytest.mark.django_db
# def test_serializes_model_fields():
#     model = SimpleModelFactory.build()
#
#     data = serialize(model, '*')
#
#     assert 'name' in data
#
#
# @pytest.mark.skip()
# @pytest.mark.django_db
# def test_serializes_properties():
#     model = SimpleModelFactory.build()
#
#     data = serialize(model, '*')
#
#     assert 'days_exists' in data
#
#
# @pytest.mark.skip()
# @pytest.mark.django_db
# def test_can_get_a_single_field():
#     model = SimpleModelFactory.build()
#
#     data = serialize(model, 'name')
#
#     assert frozenset(data.keys()) == frozenset((
#         'name',
#     ))
#
#
# @pytest.mark.skip()
# @pytest.mark.django_db
# def test_doesnt_serialize_related_if_not_expanded_in_fieldspec():
#     person = PersonFactory()
#     BlogPostFactory(author=person)
#     BlogPostFactory(author=person)
#     BlogPostFactory(author=person)
#
#     data = serialize(person, '*')
#
#     assert 'blog_posts' in data
#     assert len(data['blog_posts']) == 0
# #
# #
# # @pytest.mark.django_db
# # def test_serializes_foreign_keys_as_empty_objects_if_not_expanded():
# #     column = ColumnFactory()
# #
# #     data = serialize(column, 'table')
# #
# #     assert 'table' in data
# #     assert data['table'] == {}
# #
# #
# # @pytest.mark.django_db
# # def test_serializes_foreign_keys_properly_when_expanded():
# #     column = ColumnFactory()
# #
# #     data = serialize(column, 'table(name)')
# #
# #     assert 'table' in data
# #     assert 'name' in data['table']
#
#
# # @pytest.mark.django_db
# # def test_serializes_related_if_expanded_in_fieldspec():
# #     table = SimpleModelFactory()
# #     ColumnFactory(table=table)
# #     ColumnFactory(table=table)
# #     ColumnFactory(table=table)
# #
# #     data = serialize(table, '*,columns(*)')
# #
# #     assert 'columns' in data
# #     assert len(data['columns']) == 3
# #     assert 'name' in data['columns'][0]
# #     assert 'type' in data['columns'][0]
# #     assert 'table' in data['columns'][0]
#
#
# @pytest.mark.skip()
# @pytest.mark.django_db
# def test_serializes_only_specified_related_fields():
#     person = PersonFactory()
#     BlogPostFactory(author=person)
#     BlogPostFactory(author=person)
#     BlogPostFactory(author=person)
#
#     data = serialize(person, '*,blog_posts(title)')
#
#     assert 'blog_posts' in data
#     assert len(data['blog_posts']) == 3
#     assert 'title' in data['blog_posts'][0]
#     assert 'content' not in data['blog_posts'][0]
#     assert 'author' not in data['blog_posts'][0]
