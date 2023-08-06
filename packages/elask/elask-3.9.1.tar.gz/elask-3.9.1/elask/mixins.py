import json
import math

import pandas as pd
from elask.manager import ESManager
from elasticsearch import Elasticsearch, helpers
from elasticsearch_dsl import A, Q, Search
from flask import send_file
from flask_restful import Api, Resource, abort, reqparse
from marshmallow import Schema


class CreateModelMixin(object):
    """
    Create a document instance.
    """
    def create(self, request):
        self.action = 'create'
        data = request.get_json()
        # audit option
        if hasattr(self, 'auto_audit'):
            data = self._save_audit_details(mode='create', data=data)
        if hasattr(self, 'pre_save'):
            data = self.pre_save(request, data=data, mode='create')
        serializer = self.get_serializer_class()(strict=True)
        try:
            errors = serializer.validate(data)
        except Exception as e:
            return abort(400, message=e.messages)
        if errors.keys():
            return abort(400, message=errors)
        else:
            payload = serializer.load(data).data
            if getattr(self, 'parent', None) is not None:
                payload = self._update_payload(request, payload)
            doc = self.model(
                _index= self.index,
                **payload
            )
        doc.save()
        if hasattr(self, 'post_save'):
            doc = self.post_save(request, doc=doc, mode='create')
        serializer = self.get_serializer_class()()
        result = doc.to_dict()
        result.update({'id': doc._id})
        data = serializer.dump(result)
        return data

    def create_with_parent(self, request, **kwargs):
        """
        If routed using parent_id
        """
        parent_id = kwargs.get(self._parent_lookup_field, None)
        if self.is_parent_exists(parent_id) is False:
            return abort(404, message="Parent id doesn't exists")
        self.parent_id_value = parent_id
        return self.create(request)

    def _update_payload(self, request, payload):
        """
        Updating parent_id field
        """
        if getattr(self, 'parent_id_value', None) is not None:
            payload.update({
                self._parent_lookup_field: self.parent_id_value
            })
        return payload


class ListModelMixin(object):
    """
    Listing documents.
    """
    def _filtering(self, params=None, serializer_fields=None):
        """
        Supports full text search on all/full_text_search[] fields
        Supports normal search field=value with AND logic
        """
        criteria = None
        if params is None or not isinstance(params, dict):
            return None # exit
        # Check for full text
        if 'search' in params and params.get('search') and params.get('search') != '' and params.get('search') != 'null':
            if not self.full_text_search:
                return None # exit
            if isinstance(self.full_text_search, list):
                serializer_fields = self.full_text_search
            for field in serializer_fields:
                if criteria is None:
                    criteria = Q("wildcard", **{field:"*{0}*".format(params.get('search'))})
                else:
                    criteria = criteria | Q("wildcard", **{field:"*{0}*".format(params.get('search'))})
        # Normal search
        if hasattr(self, 'search_fields') and self.search_fields and isinstance(self.search_fields, list):
            for field in self.search_fields:
                if field not in params and params.get(field) == "" or params.get(field) is None:
                    continue # if search field value not provided
                if criteria is None:
                    criteria = Q("wildcard", **{field:"*{0}*".format(params.get(field))})
                else:
                    criteria = criteria & Q("wildcard", **{field:"*{0}*".format(params.get(field))})
        return criteria        

    def list(self, request, *args, **kwargs):
        params = request.args.copy()
        self.action = 'list'
        criteria = None
        # Get page_size
        try:
            page_size = int(params.get('page_size', 100))
        except Exception as general_exception:
            page_size = 100
        # Get page
        try:
            page = int(params.get('page', 1))
        except Exception as general_exception:
            page = 1
        # Get Sort
        try:
            sort = params.get('sort', None)
        except:
            sort = None
        # Get Format
        try:
            _format = params.get('format', 'json')
        except:
            _format = 'json'
        client = ESManager().client
        search = Search(
            index=self.index,
            doc_type=self.doc_type
        ).using(client)
        if _format == 'csv':
            _from = 0
            size = 10000 # Max results
        else:
            _from = abs(page - 1) * page_size
            size = page * page_size
        serializer_klass = self.get_serializer_class()
        serializer = serializer_klass(many=True)
        # Check for parent
        if getattr(self, 'parent', None) is not None:
            criteria = self._update_criteria_with_parent(request)
        filtering_criteria = self._filtering(params=params, serializer_fields=serializer_klass.Meta.fields)
        if filtering_criteria is not None:
            criteria = filtering_criteria & criteria if criteria is not None else filtering_criteria
        search_instance = search.query() if criteria is None else search.query(criteria)
        if sort is None:
            data = search_instance[_from:size].execute().to_dict()['hits']
        else:
            data = search_instance.sort(sort)[_from:size].execute().to_dict()['hits']
        total = data['total']
        end_num = (page) * page_size
        start_num = (abs(page - 1) * page_size) + 1
        next_page = page + 1
        if end_num >= total:
            end_num = total
            next_page = None
        if page == 1:
            previous_page = None
        else:
            previous_page = page - 1
        results = []
        for item in data['hits']:
            temp = item['_source']
            temp.update({'id': item['_id']})
            results.append(temp)
        data = serializer.dumps(results)
        if _format == 'csv':
            _columns = serializer_klass.Meta.fields
            _header = None
            if hasattr(self, 'download') and isinstance(self.download, dict):
                if 'columns' in self.download and isinstance(self.download['columns'], list) and self.download['columns']:
                    _columns = self.download['columns']
                if 'header' in self.download and isinstance(self.download['header'], list) and self.download['header']:
                    _header = self.download['header']
            if not _header:
                _header = [heading.replace("_", " ").title() for heading in _columns]
            if len(_columns) != len(_header):
                _header = _header[:len(_columns)]
            output_df = pd.DataFrame(json.loads(data.data))
            output = output_df.to_csv(
                header=_header,
                columns=_columns,
                index=False
            )
            return output # exit
        output = {
            'current_page': page,
            'page_size': page_size,
            'start_num': start_num,
            'end_num': end_num,
            'results': json.loads(data.data),
            'total_num': total,
            'previous_page': previous_page,
            'next_page': next_page,
            'last_page': int(math.ceil(total / float(page_size)))
        }
        return output # exit

    def list_with_parent(self, request, *args, **kwargs):
        parent_id = kwargs.get(self._parent_lookup_field, None)
        if self.is_parent_exists(parent_id) is False:
            return abort(404, message="Parent id doesn't exists")
        self.parent_id_value = parent_id
        return self.list(request, *args, **kwargs)

    def _update_criteria_with_parent(self, request):
        return Q("match", **{
            self._parent_lookup_field: self.parent_id_value
        })


class RetrieveModelMixin(object):
    """
    Retrieve a document instance.
    """
    
    def retrieve(self, request, *args, **kwargs):
        self.action = 'retrieve'
        params = request.args.copy()
        pk = kwargs.get(self._lookup_field)
        try:
            doc = self.model.get(**{
                'index':self.index,
                self.lookup_field:pk
            })
            # Post check the parent
            if getattr(self, 'parent', None) is not None:
                if doc.to_dict().get(self._parent_lookup_field, None) != self.parent_id_value:
                    raise ValueError
        except Exception as ex:
            return abort(404, message="Record Not Found")
        result = doc.to_dict()
        result.update({'id': doc._id})
        serializer = self.get_serializer_class()()
        data = serializer.dump(result)
        return data
    
    def retrieve_with_parent(self, request, *args, **kwargs):
        parent_id = kwargs.get(self._parent_lookup_field, None)
        if self.is_parent_exists(parent_id) is False:
            return abort(404, message="Parent id doesn't exists")
        self.parent_id_value = parent_id
        return self.retrieve(request, *args, **kwargs)


class UpdateModelMixin(object):
    """
    Update a document instance.
    """
    def update(self, request, *args, **kwargs):
        self.action = 'update'
        data = request.get_json()
        pk = kwargs.get(self._lookup_field, None)
        try:
            doc = self.model.get(**{
                'index':self.index,
                self.lookup_field:pk
            })
            # Post check the parent
            if getattr(self, 'parent', None) is not None:
                if doc.to_dict().get(self._parent_lookup_field, None) != self.parent_id_value:
                    raise ValueError
        except Exception as ex:
            return abort(404, message="Record Not Found")
        # audit option
        if hasattr(self, 'auto_audit'):
            data = self._save_audit_details(mode='update', data=data)
        if hasattr(self, 'pre_save'):
            data = self.pre_save(request, data=data, mode='update')
        doc.update(**data)
        doc.save()
        if hasattr(self, 'post_save'):
            doc = self.post_save(request, doc=doc, mode='update')
        result = doc.to_dict()
        result.update({'id': doc._id})
        serializer = self.get_serializer_class()()
        data = serializer.dump(result)
        return data

    def update_with_parent(self, request, *args, **kwargs):
        parent_id = kwargs.get(self._parent_lookup_field, None)
        if self.is_parent_exists(parent_id) is False:
            return abort(404, message="Parent id doesn't exists")
        self.parent_id_value = parent_id
        return self.update(request, *args, **kwargs)

class DestroyModelMixin(object):
    """
    Destroy a document
    """
    def destroy(self, request, *args, **kwargs):
        self.action = 'destroy'
        pk = kwargs.get(self._lookup_field, None)
        try:
            doc = self.model.get(**{
                'index':self.index,
                self.lookup_field:pk
            })
            if getattr(self, 'parent', None) is not None:
                if doc.to_dict().get(self._parent_lookup_field, None) != self.parent_id_value:
                    raise ValueError
        except Exception as ex:
            return abort(404, message="Record Not Found")
        if hasattr(self, 'pre_delete'):
            self.pre_delete(doc=doc)
        self.perform_destroy(doc)
        if hasattr(self, 'post_delete'):
            self.post_delete(doc=doc)
        return "Deleted Successfully"

    def perform_destroy(self, doc):
        doc.delete()

    def destroy_with_parent(self, request, *args, **kwargs):
        parent_id = kwargs.get(self._parent_lookup_field, None)
        if self.is_parent_exists(parent_id) is False:
            return abort(404, message="Parent id doesn't exists")
        self.parent_id_value = parent_id
        return self.delete(request, *args, **kwargs)
