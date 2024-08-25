from sqlalchemy import Column, ForeignKey, Index, text
from sqlalchemy.sql.sqltypes import Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from src.database import engine, Base


class FundUsers(Base):
    __tablename__ = 'fund_users'

    fund_id = Column(Integer, ForeignKey('vc_fund.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)

    fund = relationship("Fund", foreign_keys=[fund_id], overlaps="users_in")
    user = relationship("User", foreign_keys=[user_id], overlaps="funds_in")


class StartupUser(Base):
    __tablename__ = 'startup_users'

    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    startup_id = Column(Integer, ForeignKey('startup.id'), primary_key=True)

    user = relationship("User", foreign_keys=[user_id], overlaps="startups")
    startup = relationship("Startup", foreign_keys=[
                           startup_id], overlaps="users")


class UserStartupFavorite(Base):
    __tablename__ = 'user_startup_favorites'

    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    startup_id = Column(Integer, ForeignKey('startup.id'), primary_key=True)

    user = relationship("User", foreign_keys=[
                        user_id], overlaps="startups_favorites")
    startup = relationship("Startup", foreign_keys=[
                           startup_id], overlaps="users_favorites")


class UserFundFavorite(Base):
    __tablename__ = 'user_fund_favorites'

    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    fund_id = Column(Integer, ForeignKey('vc_fund.id'), primary_key=True)

    user = relationship("User", foreign_keys=[user_id], overlaps="funds")
    fund = relationship("Fund", foreign_keys=[fund_id], overlaps="users")


class FundSector(Base):
    __tablename__ = 'fund_sectors'

    fund_id = Column(Integer, ForeignKey('vc_fund.id'), primary_key=True)
    sector_id = Column(Integer, ForeignKey('sector.id'), primary_key=True)

    fund = relationship("Fund", foreign_keys=[fund_id], overlaps="sectors")
    sector = relationship("Sector", foreign_keys=[sector_id], overlaps="funds")


class FundCheckSize(Base):
    __tablename__ = 'fund_check_size'

    fund_id = Column(Integer, ForeignKey('vc_fund.id'), primary_key=True)
    check_size_id = Column(Integer, ForeignKey(
        'check_size.id'), primary_key=True)

    fund = relationship("Fund", foreign_keys=[fund_id], overlaps="check_size")
    check_size = relationship("CheckSize", foreign_keys=[
                              check_size_id], overlaps="funds")


class FundPartner(Base):
    __tablename__ = 'fund_partners'

    fund_id = Column(Integer, ForeignKey('vc_fund.id'), primary_key=True)
    partner_id = Column(Integer, ForeignKey('vc_partner.id'), primary_key=True)

    fund = relationship("Fund", foreign_keys=[fund_id], overlaps="partners")
    partner = relationship("Partner", foreign_keys=[
                           partner_id], overlaps="funds")


class FundCountry(Base):
    __tablename__ = 'fund_countries'

    fund_id = Column(Integer, ForeignKey('vc_fund.id'), primary_key=True)
    country_id = Column(Integer, ForeignKey('country.id'), primary_key=True)

    fund = relationship("Fund", foreign_keys=[fund_id], overlaps="countries")
    country = relationship("Country", foreign_keys=[
                           country_id], overlaps="funds")


class FundRound(Base):
    __tablename__ = 'fund_rounds'

    fund_id = Column(Integer, ForeignKey('vc_fund.id'), primary_key=True)
    round_id = Column(Integer, ForeignKey('round.id'), primary_key=True)

    fund = relationship("Fund", foreign_keys=[fund_id], overlaps="rounds")
    round = relationship("Round", foreign_keys=[round_id], overlaps="fund")


class InvestorRound(Base):
    __tablename__ = 'investor_rounds'

    investor_id = Column(Integer, ForeignKey(
        'vc_investor.id'), primary_key=True)
    round_id = Column(Integer, ForeignKey('round.id'), primary_key=True)

    investor = relationship("Investor", foreign_keys=[
                            investor_id], overlaps="rounds")
    round = relationship("Round", foreign_keys=[round_id], overlaps="investor")


class Traction(Base):
    __tablename__ = 'traction'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    startups = relationship("Startup", back_populates="traction")


class Partner(Base):
    __tablename__ = 'vc_partner'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    role = Column(String(255), nullable=True)
    photo = Column(String(255), nullable=True)
    email = Column(String(200), nullable=True)
    twitter = Column(String(255), nullable=True)
    linkedin = Column(String(255), nullable=True)
    crunch_base = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    vc_link = Column(String(255), nullable=True)

    funds = relationship("Fund", secondary="fund_partners",
                         back_populates='partners', overlaps="fund")


class CheckSize(Base):
    __tablename__ = 'check_size'
    id = Column(Integer, primary_key=True)
    size = Column(String(100), nullable=False)

    funds = relationship("Fund", secondary="fund_check_size",
                         back_populates='check_size', overlaps="fund")


class Country(Base):
    __tablename__ = 'country'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    funds = relationship("Fund", secondary="fund_countries",
                         back_populates='countries', overlaps="fund")

    startups = relationship("Startup", back_populates="country")


class Sector(Base):
    __tablename__ = 'sector'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    funds = relationship("Fund", secondary="fund_sectors",
                         back_populates='sectors', overlaps="fund")

    startups = relationship("Startup", back_populates="sector")


class Round(Base):
    __tablename__ = "round"
    id = Column(Integer, primary_key=True)
    stage = Column(String(200), nullable=False)

    user = relationship("User", back_populates="stage_round")
    investor = relationship("Investor", secondary="investor_rounds",
                            back_populates='rounds', overlaps="investor")
    fund = relationship("Fund", secondary="fund_rounds",
                        back_populates='rounds', overlaps="fund")

    startup = relationship("Startup", back_populates="round")


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    email = Column(String(200), unique=True, index=True, nullable=False)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    nickname = Column(String(255), nullable=True)
    contact_email = Column(String(255), nullable=True)
    country_code = Column(String(10), nullable=True)
    phone_number = Column(String(20), nullable=True)
    followers_amount = Column(Integer, nullable=False, default=0)
    industry = Column(String(255), nullable=True, unique=False)
    summary = Column(Text, nullable=True, unique=False)
    role = Column(Text, nullable=True, unique=False)
    headline = Column(Text, nullable=True, unique=False)
    linkedin_url = Column(String(255), nullable=True, unique=True)
    location = Column(String(255), nullable=True)
    seeking_capital = Column(Boolean, nullable=True)
    photo_url = Column(String(255), nullable=True)
    startup_url = Column(String(255), nullable=True)
    main_industry = Column(String(255), nullable=True)
    ecosystem_role = Column(String(255), nullable=True)
    investment_geography = Column(String(255), nullable=True)
    industry_to_invest = Column(String(255), nullable=True)
    check_size = Column(String(255), nullable=True)
    job_level = Column(String(255), nullable=True)
    terms_conditions = Column(Boolean, nullable=True)
    investment_stage = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False,
                        default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)

    round_id = Column(Integer, ForeignKey("round.id"))
    stage_round = relationship("Round", back_populates="user")

    education = relationship("Education", back_populates="user")
    experience = relationship("Experience", back_populates="user")

    funds = relationship("Fund", secondary="user_fund_favorites",
                         back_populates="users", overlaps="fund")

    funds_in = relationship("Fund", secondary="fund_users",
                            back_populates='users_in', overlaps="fund")

    startups = relationship("Startup", secondary="startup_users",
                            back_populates="users", overlaps="startup")
    startups_favorites = relationship(
        "Startup", secondary="user_startup_favorites", back_populates="users_favorites", overlaps="startup")

    courses = relationship(
        "Course", secondary="user_courses", back_populates="users")
    classes = relationship(
        "Class", secondary="user_classes", back_populates="users")


class Education(Base):
    __tablename__ = "education"
    id = Column(Integer, primary_key=True)
    degree_name = Column(String(200), nullable=True)
    grade = Column(String(200), nullable=True)
    school_name = Column(String(200), nullable=False)
    linkedin_url = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="education")


class Experience(Base):
    __tablename__ = "experience"
    id = Column(Integer, primary_key=True)
    company = Column(String(200), nullable=False)
    location = Column(String(255), nullable=True)
    linkedin_url = Column(String(255), nullable=False)
    role = Column(String(200), nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    description = Column(Text, nullable=True)

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="experience")


class Reporter(Base):
    __tablename__ = "vc_reporter"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    photo = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    email = Column(String(200), nullable=True)
    twitter = Column(String(255), nullable=True)
    linkedin = Column(String(255), nullable=True)
    channel_url = Column(String(255), nullable=True)
    channel_image = Column(String(255), nullable=True)
    location = Column(String(50), nullable=True)
    company = Column(String(50), nullable=True)


class Investor(Base):
    __tablename__ = "vc_investor"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    photo = Column(String(255), nullable=True)
    role = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    email = Column(String(255), nullable=True)
    twitter = Column(Text, nullable=True)
    linkedin = Column(Text, nullable=True)
    crunch_base = Column(Text, nullable=True)
    youtube = Column(Text, nullable=True)

    rounds = relationship("Round", secondary="investor_rounds",
                          back_populates='investor', overlaps="round")


class Fund(Base):
    __tablename__ = "vc_fund"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    photo = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True, unique=True)
    is_visible = Column(Boolean, nullable=False, default=True)
    twitter = Column(String(255), nullable=True)
    linkedin = Column(String(255), nullable=True, unique=True)
    crunch_base = Column(String(255), nullable=True)
    contact = Column(String(255), nullable=True)
    location = Column(String(50), nullable=True)

    rounds = relationship("Round", secondary="fund_rounds",
                          back_populates='fund', overlaps="round")
    countries = relationship(
        "Country", secondary="fund_countries", back_populates='funds', overlaps="country")
    partners = relationship("Partner", secondary="fund_partners",
                            back_populates='funds', overlaps="partner")
    sectors = relationship("Sector", secondary="fund_sectors",
                           back_populates='funds', overlaps="sector")
    check_size = relationship("CheckSize", secondary="fund_check_size",
                              back_populates='funds', overlaps="check_size")
    users = relationship("User", secondary="user_fund_favorites",
                         back_populates='funds', overlaps="user")

    users_in = relationship("User", secondary="fund_users",
                            back_populates='funds_in', overlaps="user")


#Index('trgm_index_vc_funds_name', Fund.name, postgresql_concurrently=True, postgresql_using='gin')


class Startup(Base):
    __tablename__ = "startup"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=True, unique=True)
    description = Column(Text, nullable=True)
    country_code = Column(String(10), nullable=True)
    phone_number = Column(String(20), nullable=True)
    website = Column(String(255), nullable=True)
    one_sentence_description = Column(String(115), nullable=True)
    linkedin = Column(String(255), nullable=True, unique=True)
    photo = Column(String(255), nullable=True)
    calendly = Column(String(255), nullable=True)
    deck = Column(String(255), nullable=True)
    fund_raised = Column(Text, nullable=True)

    country_id = Column(Integer, ForeignKey("country.id"))
    sector_id = Column(Integer, ForeignKey("sector.id"))
    round_id = Column(Integer, ForeignKey("round.id"))
    traction_id = Column(Integer, ForeignKey("traction.id"))

    country = relationship("Country", back_populates="startups")

    sector = relationship("Sector", back_populates="startups")

    round = relationship("Round", back_populates="startup")

    users = relationship("User", secondary="startup_users",
                         back_populates="startups", overlaps="user")

    traction = relationship("Traction", back_populates="startups")

    users_favorites = relationship(
        "User", secondary="user_startup_favorites", back_populates="startups_favorites", overlaps="user")


class CrmInvestorInvestRange(Base):
    __tablename__ = "crm_investor_invest_range"

    crm_investor_id = Column(Integer, ForeignKey(
        "crm_investor.id"), primary_key=True)
    crm_invest_range_id = Column(Integer, ForeignKey(
        "crm_invest_range.id"), primary_key=True)

    crm_investor = relationship("CrmInvestor", back_populates="invest_ranges")
    crm_invest_range = relationship(
        "CrmInvestRange", back_populates="crm_investors")


class CrmInvestorSectorAndStage(Base):
    __tablename__ = "crm_investor_sector_and_stage"

    crm_investor_id = Column(Integer, ForeignKey(
        "crm_investor.id"), primary_key=True)
    crm_sector_and_stage_id = Column(Integer, ForeignKey(
        "crm_sector_and_stage.id"), primary_key=True)

    crm_investor = relationship(
        "CrmInvestor", back_populates="sector_and_stages")
    crm_sector_and_stage = relationship(
        "CrmSectorAndStage", back_populates="crm_investors")


class CrmInvestRange(Base):
    __tablename__ = "crm_invest_range"
    id = Column(Integer, primary_key=True)
    range = Column(String(100), nullable=False)

    crm_investors = relationship(
        "CrmInvestorInvestRange", back_populates="crm_invest_range")


class CrmSectorAndStage(Base):
    __tablename__ = "crm_sector_and_stage"
    id = Column(Integer, primary_key=True)
    sector = Column(String(100), nullable=False)
    stage = Column(String(100), nullable=False)

    crm_investors = relationship(
        "CrmInvestorSectorAndStage", back_populates="crm_sector_and_stage")


class CrmInvestor(Base):
    __tablename__ = "crm_investor"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    location = Column(String(100), nullable=True)
    role = Column(Text, nullable=True)
    vc_link = Column(String(255), nullable=True)
    photo = Column(Text, nullable=True)
    linkedin_investor = Column(Text, nullable=True)

    invest_ranges = relationship(
        "CrmInvestorInvestRange", back_populates="crm_investor")
    sector_and_stages = relationship(
        "CrmInvestorSectorAndStage", back_populates="crm_investor")


# COURSE MODELS

class UserClass(Base):
    __tablename__ = "user_classes"
    id = Column(Integer, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    class_id = Column(Integer, ForeignKey("class.id"), primary_key=True)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", foreign_keys=[user_id], overlaps="classes")
    class_ = relationship("Class", foreign_keys=[class_id], overlaps="users")


class UserCourse(Base):
    __tablename__ = "user_courses"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    course_id = Column(Integer, ForeignKey("course.id"), primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
    user = relationship("User", foreign_keys=[user_id], overlaps="courses")
    course = relationship("Course", foreign_keys=[course_id], overlaps="users")


class Course(Base):
    __tablename__ = "course"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True)
    photo = Column(String(255))
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    users = relationship("User", secondary="user_courses",
                         back_populates="courses")
    modules = relationship("Module", back_populates="course")
    events = relationship("Event", back_populates="course")


class Module(Base):
    __tablename__ = "module"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True)
    previous_id = Column(Integer)
    next_id = Column(Integer)
    course_id = Column(Integer, ForeignKey("course.id"))
    course = relationship("Course", back_populates="modules")
    classes = relationship("Class", back_populates="module")
    created_at = Column(DateTime, server_default=func.now())


class Class(Base):
    __tablename__ = "class"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True, unique=True)
    video_link = Column(String(255))
    description = Column(Text)
    previous_id = Column(Integer)
    next_id = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
    module_id = Column(Integer, ForeignKey("module.id"))
    module = relationship("Module", back_populates="classes")
    users = relationship("User", secondary="user_classes",
                         back_populates="classes")


class Event(Base):
    __tablename__ = "event"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    event_date = Column(DateTime, nullable=False)
    description = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    course_id = Column(Integer, ForeignKey("course.id"))
    course = relationship("Course", back_populates="events")


Base.metadata.create_all(bind=engine)

# def create_concurrent_index():
#     connection = engine.connect()
#     connection.execution_options(isolation_level="AUTOCOMMIT")

#     try:
#         connection.execute(text(
#             "CREATE INDEX CONCURRENTLY IF NOT EXISTS trgm_index_vc_funds_name ON vc_fund USING gin (lower(name) gin_trgm_ops);"
#         ))
#     finally:
#         connection.close()

# create_concurrent_index()
