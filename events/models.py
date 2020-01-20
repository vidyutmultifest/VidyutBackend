import uuid
from django.db import models
from ckeditor.fields import RichTextField
from django.utils import timezone
from django.contrib.auth.models import User

to_tz = timezone.get_default_timezone()


class Category(models.Model):
    def get_image_path(self, filename):
        ext = filename.split('.')[-1]
        filename = 'vidyut_event_cat_' + "%s.%s" % (uuid.uuid4(), ext)
        return 'static/events/categories/' + filename
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    icon = models.ImageField(upload_to=get_image_path, null=True, blank=True)
    listingWeight = models.SmallIntegerField(null=True, blank=True)

    def __str__(self):
        return self.name


class Partners(models.Model):
    def get_image_path(self, filename):
        ext = filename.split('.')[-1]
        filename = 'vidyut_partner_' + "%s.%s" % (uuid.uuid4(), ext)
        return 'static/events/partners/' + filename

    name = models.CharField(max_length=200)
    about = RichTextField(null=True, blank=True)
    logo = models.ImageField(upload_to=get_image_path, null=True, blank=True)

    def __str__(self):
        return self.name


class Trainer(models.Model):
    def get_image_path(self, filename):
        ext = filename.split('.')[-1]
        filename = 'vidyut_trainer_' + "%s.%s" % (uuid.uuid4(), ext)
        return 'static/events/trainers/' + filename

    name = models.CharField(max_length=50)
    photo = models.ImageField(upload_to=get_image_path, null=True, blank=True)
    about = RichTextField(null=True, blank=True)

    def __str__(self):
        return self.name


class ContactPerson(models.Model):
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    def __str__(self):
        return self.name


class Venue(models.Model):
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name


class TimeSlot(models.Model):
    startTime = models.DateTimeField()
    endTime = models.DateTimeField()

    def __str__(self):
        return self.startTime.astimezone(to_tz).strftime("%d/%m, %H:%M") + ' - ' + self.endTime.astimezone(to_tz).strftime("%d/%m, %H:%M")


class Department(models.Model):
    def get_image_path(self, filename):
        ext = filename.split('.')[-1]
        filename = 'vidyut_department_' + "%s.%s" % (uuid.uuid4(), ext)
        return 'static/events/departments/' + filename

    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    icon = models.ImageField(upload_to=get_image_path, null=True, blank=True)

    def __str__(self):
        return self.name


class Ticket(models.Model):
    def get_image_path(self, filename):
        ext = filename.split('.')[-1]
        filename = 'vidyut_ticket_' + "%s.%s" % (uuid.uuid4(), ext)
        return 'static/events/covers/' + filename

    def get_poster_path(self, filename):
        ext = filename.split('.')[-1]
        filename = 'vidyut_workshop_' + "%s.%s" % (uuid.uuid4(), ext)
        return 'static/events/posters/' + filename

    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, null=True, blank=True)
    organiser = models.ForeignKey(Partners, on_delete=models.PROTECT, related_name='TicketEventOrganizer', null=True, blank=True)
    cover = models.ImageField(upload_to=get_image_path, null=True, blank=True)
    poster = models.ImageField(upload_to=get_poster_path, null=True, blank=True)
    description = models.CharField(max_length=350, null=True, blank=True)
    details = RichTextField(null=True, blank=True)
    fee = models.PositiveIntegerField(null=True, blank=True)
    contacts = models.ManyToManyField(ContactPerson, blank=True)
    schedule = models.ManyToManyField(TimeSlot, through='TicketSchedule', blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    lastEditor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    lastEditTime = models.DateTimeField(null=True, blank=True)
    isRecommended = models.BooleanField(default=False)
    isPublished = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Merchandise(models.Model):
    def get_image_path(self, filename):
        ext = filename.split('.')[-1]
        filename = 'vidyut_merchandise_' + "%s.%s" % (uuid.uuid4(), ext)
        return 'static/events/covers/' + filename

    def get_poster_path(self, filename):
        ext = filename.split('.')[-1]
        filename = 'vidyut_workshop_' + "%s.%s" % (uuid.uuid4(), ext)
        return 'static/events/posters/' + filename

    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    cover = models.ImageField(upload_to=get_image_path, null=True, blank=True)
    poster = models.ImageField(upload_to=get_poster_path, null=True, blank=True)
    description = models.CharField(max_length=350, null=True, blank=True)
    details = RichTextField(null=True, blank=True)
    fee = models.PositiveIntegerField(null=True, blank=True)
    contacts = models.ManyToManyField(ContactPerson, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    lastEditor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    lastEditTime = models.DateTimeField(null=True, blank=True)
    isRecommended = models.BooleanField(default=False)
    isPublished = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Workshop(models.Model):
    def get_image_path(self, filename):
        ext = filename.split('.')[-1]
        filename = 'vidyut_workshop_' + "%s.%s" % (uuid.uuid4(), ext)
        return 'static/events/covers/' + filename

    def get_poster_path(self, filename):
        ext = filename.split('.')[-1]
        filename = 'vidyut_workshop_' + "%s.%s" % (uuid.uuid4(), ext)
        return 'static/events/posters/' + filename

    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    cover = models.ImageField(upload_to=get_image_path, null=True, blank=True)
    poster = models.ImageField(upload_to=get_poster_path, null=True, blank=True)

    organiser = models.ForeignKey(Partners, on_delete=models.PROTECT, related_name='WokshopOrganizer', null=True, blank=True)
    partners = models.ManyToManyField(Partners, related_name='WorkshopPartners', blank=True)
    trainers = models.ManyToManyField(Trainer, related_name='WorkshopTrainers', blank=True)
    accreditedBy = models.ForeignKey(Partners, on_delete=models.PROTECT, related_name='WorkshopAccreditior', null=True, blank=True)
    dept = models.ForeignKey(Department, on_delete=models.PROTECT, null=True, blank=True)

    description = models.CharField(max_length=350, null=True, blank=True)
    certificate = models.CharField(max_length=500, null=True, blank=True)
    mediumOfInstruction = models.CharField(max_length=150, null=True, blank=True)
    eligibility = RichTextField(null=True, blank=True)
    syllabus = RichTextField(null=True, blank=True)
    details = RichTextField(null=True, blank=True)

    KTUActivityPoints = models.PositiveIntegerField(null=True, blank=True)
    fee = models.PositiveIntegerField(null=True, blank=True)

    contacts = models.ManyToManyField(ContactPerson, blank=True)
    schedule = models.ManyToManyField(TimeSlot, through='WorkshopSchedule', blank=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    lastEditor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    lastEditTime = models.DateTimeField(null=True, blank=True)

    isRecommended = models.BooleanField(default=False)
    isPublished = models.BooleanField(default=False)

    formFields = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Competition(models.Model):
    def get_image_path(self, filename):
        ext = filename.split('.')[-1]
        filename = 'vidyut_competition_' + "%s.%s" % (uuid.uuid4(), ext)
        return 'static/events/covers/' + filename

    def get_poster_path(self, filename):
        ext = filename.split('.')[-1]
        filename = 'vidyut_competition_' + "%s.%s" % (uuid.uuid4(), ext)
        return 'static/events/posters/' + filename

    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    cover = models.ImageField(upload_to=get_image_path, null=True, blank=True)
    poster = models.ImageField(upload_to=get_poster_path, null=True, blank=True)

    dept = models.ForeignKey(Department, on_delete=models.PROTECT, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, null=True, blank=True)
    organiser = models.ForeignKey(Partners, on_delete=models.PROTECT, related_name='CompetitionOrganizer', null=True, blank=True)
    partners = models.ManyToManyField(Partners, related_name='CompetitionPartners', blank=True)

    description = models.CharField(max_length=350, null=True, blank=True)
    details = RichTextField(null=True, blank=True)
    judgingCriteria = RichTextField(null=True, blank=True)
    rules = RichTextField(null=True, blank=True)
    KTUActivityPoints = models.PositiveIntegerField(null=True, blank=True)

    fee = models.PositiveIntegerField(null=True, blank=True)

    totalPrize = models.CharField(max_length=150, null=True, blank=True)
    firstPrize = models.CharField(max_length=150, null=True, blank=True)
    secondPrize = models.CharField(max_length=150, null=True, blank=True)
    thirdPrize = models.CharField(max_length=150, null=True, blank=True)
    otherPrizes = models.CharField(max_length=250, null=True, blank=True)

    contacts = models.ManyToManyField(ContactPerson, blank=True)

    schedule = models.ManyToManyField(TimeSlot, through='CompetitionSchedule', blank=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    lastEditor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    lastEditTime = models.DateTimeField(null=True, blank=True)

    isRecommended = models.BooleanField(default=False)
    isPublished = models.BooleanField(default=False)

    isTeamEvent = models.BooleanField(default=False)
    isTotalRate = models.BooleanField(default=True)
    minTeamSize = models.PositiveIntegerField(null=True, blank=True)
    maxTeamSize = models.PositiveIntegerField(null=True, blank=True)
    hasSelectionProcess = models.BooleanField(default=False)

    formFields = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class CompetitionSchedule(models.Model):
    slot = models.ForeignKey(TimeSlot, on_delete=models.PROTECT)
    venue = models.ForeignKey(Venue, on_delete=models.SET_NULL, blank=True, null=True)
    event = models.ForeignKey(Competition, on_delete=models.PROTECT)


class WorkshopSchedule(models.Model):
    slot = models.ForeignKey(TimeSlot, on_delete=models.PROTECT)
    venue = models.ForeignKey(Venue, on_delete=models.SET_NULL, blank=True, null=True)
    event = models.ForeignKey(Workshop, on_delete=models.PROTECT)


class TicketSchedule(models.Model):
    slot = models.ForeignKey(TimeSlot, on_delete=models.PROTECT)
    venue = models.ForeignKey(Venue, on_delete=models.SET_NULL, blank=True, null=True)
    event = models.ForeignKey(Ticket, on_delete=models.PROTECT)
