import datetime
import json
from django.utils.timezone import utc
from django.test import TestCase
from django.contrib.auth.models import User
from blogging.models import Post, Category

# Create your tests here.
class PostTestCase(TestCase):
    fixtures = [
        "blogging_test_fixture.json",
    ]

    def setUp(self):
        self.user = User.objects.get(pk=1)

    def test_string_representation(self):
        expected = "This is a title"
        p1 = Post(title=expected)
        actual = str(p1)
        self.assertEqual(expected, actual)


# and the test case and test
class CategoryTestCase(TestCase):
    def test_string_representation(self):
        expected = "A Category"
        c1 = Category(name=expected)
        actual = str(c1)
        self.assertEqual(expected, actual)


class FrontEndTestCase(TestCase):
    """test views provided in the front-end"""

    fixtures = [
        "blogging_test_fixture.json",
    ]

    def setUp(self):
        self.now = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.timedelta = datetime.timedelta(15)
        author = User.objects.get(pk=1)
        for count in range(1, 11):
            post = Post(title="Post %d Title" % count, text="foo", author=author)
            if count < 6:
                # publish the first five posts
                pubdate = self.now - self.timedelta * count
                post.published_date = pubdate
            post.save()

    def test_list_only_published(self):
        resp = self.client.get("/")
        # the content of the rendered response is always a bytestring
        resp_text = resp.content.decode(resp.charset)
        self.assertTrue("My Cooler Blog Posts" in resp_text)
        for count in range(1, 11):
            title = "Post %d Title" % count
            if count < 6:
                self.assertContains(resp, title, count=1)
            else:
                self.assertNotContains(resp, title)

    def test_details_only_published(self):
        for count in range(1, 11):
            title = "Post %d Title" % count
            post = Post.objects.get(title=title)
            resp = self.client.get("/posts/%d/" % post.pk)
            if count < 6:
                self.assertEqual(resp.status_code, 200)
                self.assertContains(resp, title)
            else:
                self.assertEqual(resp.status_code, 404)


class RestApiTestCase(TestCase):
    fixtures = [
        "blogging_test_fixture.json",
    ]

    def setUp(self):
        self.now = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.timedelta = datetime.timedelta(15)
        author = User.objects.get(pk=1)

        # create category to test category api
        category = Category(name="Fake category", description="Testing api")
        category.save()

        for count in range(1, 11):
            post = Post(title="Post %d Title" % count, text="foo", author=author)
            
            if count < 6:
                # publish the first five posts
                pubdate = self.now - self.timedelta * count
                post.published_date = pubdate    
                
            post.save()
            category.posts.add(post)
            post.save()


    def test_returned_api_users(self):
        resp = self.client.get("/api/users/")
        resp_text = resp.content.decode(resp.charset)
        json_text = json.loads(resp_text)['results']
        self.assertTrue(json_text[0]['username'] == "admin")
        self.assertTrue(json_text[0]['url'] == "http://testserver/users/1/")
        self.assertTrue(json_text[1]['username'] == "noname")
        self.assertTrue(json_text[1]['url'] == "http://testserver/users/2/")

    def test_returned_api_posts(self):
        resp = self.client.get("/api/posts/")
        resp_text = resp.content.decode(resp.charset)
        json_text = json.loads(resp_text)['results']
        self.assertTrue(len(json_text) == 10)
        for post in json_text:
            self.assertTrue('url' in post.keys())
            self.assertTrue('title' in post.keys())
            self.assertTrue('text' in post.keys())
            self.assertTrue('author' in post.keys())
            self.assertTrue('created_date' in post.keys())
            self.assertTrue('modified_date' in post.keys())
            self.assertTrue('published_date' in post.keys())
            self.assertTrue('categories' in post.keys())

    def test_returned_api_categories(self):
        resp = self.client.get("/api/categories/")
        resp_text = resp.content.decode(resp.charset)
        json_text = json.loads(resp_text)['results']
        print(json_text)
        self.assertTrue(len(json_text[0]['posts']) == 10)

