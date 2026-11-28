from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Q, Sum
from django.views.generic import TemplateView

from accounts.models import CustomUser
from agreements.models import Section, Stall, Vendor
from payments.models import Payment

Role = CustomUser.Role
MANAGER_ROLES = (Role.ADMIN, Role.STAFF)


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role in MANAGER_ROLES


class ReportIndexView(StaffRequiredMixin, TemplateView):
    template_name = "reports/index.html"


class OccupancyReportView(StaffRequiredMixin, TemplateView):
    template_name = "reports/occupancy.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        rows = list(
            Stall.objects.values("section__location__name", "section__name", "stall_type__name")
            .annotate(
                total=Count("pk"),
                occupied=Count("pk", filter=Q(status=Stall.OCCUPIED)),
                available=Count("pk", filter=Q(status=Stall.AVAILABLE)),
                maintenance=Count("pk", filter=Q(status=Stall.MAINTENANCE)),
            )
            .order_by("section__location__name", "section__name", "stall_type__name")
        )
        for r in rows:
            r["rate"] = round(100 * r["occupied"] / r["total"], 1) if r["total"] else 0
        totals = {k: sum(r[k] for r in rows) for k in ("total", "occupied", "available", "maintenance")}
        totals["rate"] = round(100 * totals["occupied"] / totals["total"], 1) if totals["total"] else 0
        ctx.update(rows=rows, totals=totals)
        return ctx


def _summarize(keys):
    rows = list(
        Payment.objects.values(*keys)
        .annotate(count=Count("pk"), due=Sum("amount_due"), paid=Sum("amount_paid"))
        .order_by(*keys)
    )
    for r in rows:
        r["balance"] = r["due"] - r["paid"]
    return rows


class PaymentReportView(StaffRequiredMixin, TemplateView):
    template_name = "reports/payments.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        monthly = _summarize(["billing_month"])
        vendors = _summarize([
            "rental_agreement__vendor__last_name",
            "rental_agreement__vendor__first_name",
            "rental_agreement__vendor_id",
        ])
        due = sum(r["due"] for r in monthly)
        paid = sum(r["paid"] for r in monthly)
        ctx.update(monthly=monthly, vendors=vendors,
                   totals={"due": due, "paid": paid, "balance": due - paid})
        return ctx


class InspectionViolationReportView(StaffRequiredMixin, TemplateView):
    template_name = "reports/inspections.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["sections"] = (
            Section.objects.select_related("location")
            .annotate(
                inspection_count=Count("stalls__inspections", distinct=True),
                failed_count=Count("stalls__inspections",
                                   filter=Q(stalls__inspections__result="FAILED"), distinct=True),
                violation_count=Count("stalls__violations", distinct=True),
            )
            .order_by("location__name", "name")
        )
        ctx["stalls"] = (
            Stall.objects.select_related("section")
            .annotate(
                inspection_count=Count("inspections", distinct=True),
                failed_count=Count("inspections", filter=Q(inspections__result="FAILED"), distinct=True),
                violation_count=Count("violations", distinct=True),
            )
            .filter(Q(inspection_count__gt=0) | Q(violation_count__gt=0))
            .order_by("stall_number")
        )
        ctx["vendors"] = (
            Vendor.objects.annotate(
                violation_count=Count("violations"),
                open_count=Count("violations", filter=Q(violations__status="OPEN")),
                fine_total=Sum("violations__fine_amount"),
            )
            .filter(violation_count__gt=0)
            .order_by("last_name", "first_name")
        )
        return ctx
