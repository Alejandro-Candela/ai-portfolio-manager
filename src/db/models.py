import enum
import uuid

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class UseCaseStatus(str, enum.Enum):
    new = "new"
    evaluating = "evaluating"
    scored = "scored"
    business_case = "business_case"
    review = "review"
    approved = "approved"
    rejected = "rejected"
    archived = "archived"


class Urgency(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class EvaluationDimension(str, enum.Enum):
    security = "security"
    feasibility = "feasibility"
    cost = "cost"
    value = "value"


class BusinessCaseRecommendation(str, enum.Enum):
    go = "go"
    no_go = "no_go"
    conditional = "conditional"


class BusinessCaseStatus(str, enum.Enum):
    draft = "draft"
    critic_review = "critic_review"
    pending_human = "pending_human"
    approved = "approved"
    rejected = "rejected"


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    slug = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)  # Entra ID OID
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    email = Column(String, nullable=False)
    display_name = Column(String, nullable=False)
    roles = Column(String, nullable=False, default="viewer")  # comma-separated
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    tenant = relationship("Tenant")

    __table_args__ = (UniqueConstraint("tenant_id", "email", name="uq_user_tenant_email"),)


class UseCase(Base):
    __tablename__ = "use_cases"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False, default="")
    problem_statement = Column(Text, nullable=False, default="")
    stakeholders = Column(Text, nullable=False, default="")  # JSON array string
    available_data = Column(Text, nullable=False, default="")
    expected_outcome = Column(Text, nullable=False, default="")
    urgency = Column(Enum(Urgency), nullable=False, default=Urgency.medium)
    status = Column(
        Enum(UseCaseStatus), nullable=False, default=UseCaseStatus.new, index=True
    )
    composite_score = Column(Float, nullable=True)
    created_by = Column(String, nullable=False)  # user id
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    evaluations = relationship("Evaluation", back_populates="use_case", cascade="all, delete-orphan")
    business_cases = relationship("BusinessCase", back_populates="use_case", cascade="all, delete-orphan")


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    use_case_id = Column(String, ForeignKey("use_cases.id"), nullable=False, index=True)
    dimension = Column(Enum(EvaluationDimension), nullable=False)
    score = Column(Float, nullable=False)
    justification = Column(Text, nullable=False)
    raw_output = Column(Text, nullable=True)
    model_used = Column(String, nullable=False, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    use_case = relationship("UseCase", back_populates="evaluations")

    __table_args__ = (
        UniqueConstraint("use_case_id", "dimension", name="uq_evaluation_use_case_dimension"),
    )


class BusinessCase(Base):
    __tablename__ = "business_cases"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    use_case_id = Column(
        String, ForeignKey("use_cases.id"), nullable=False, index=True, unique=True
    )
    executive_summary = Column(Text, nullable=False, default="")
    problem_and_opportunity = Column(Text, nullable=False, default="")
    proposed_solution = Column(Text, nullable=False, default="")
    cost_benefit_analysis = Column(Text, nullable=False, default="")
    risks_and_mitigations = Column(Text, nullable=False, default="")
    timeline = Column(Text, nullable=False, default="")
    recommendation = Column(
        Enum(BusinessCaseRecommendation), nullable=False, default=BusinessCaseRecommendation.conditional
    )
    status = Column(
        Enum(BusinessCaseStatus), nullable=False, default=BusinessCaseStatus.draft
    )
    langgraph_thread_id = Column(String, nullable=True)  # for HITL resume
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    use_case = relationship("UseCase", back_populates="business_cases")


class ScoringConfig(Base):
    __tablename__ = "scoring_configs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False, index=True)
    dimension = Column(Enum(EvaluationDimension), nullable=False)
    weight = Column(Float, nullable=False, default=0.25)

    __table_args__ = (
        UniqueConstraint("tenant_id", "dimension", name="uq_scoring_config_tenant_dimension"),
    )


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    tenant_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False)
    action = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    resource_id = Column(String, nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
