# pyright: reportAttributeAccessIssue=false, reportArgumentType=false, reportIncompatibleMethodOverride=false
from types import SimpleNamespace

from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, ListView, View

from .calc import CalculationError, compute_line  # type: ignore[import-unresolved]
from .forms import CableCalForm, CableLineItemFormSet, ReelsListForm, TransportListForm
from .models import CableCal, CableLineItem, CalculationSettings, ReelsList, TransportList


class CableCalView(View):
    """Enter a multi-line cable order and compute reel allocation per line."""

    template_name = "app/cable_cal.html"

    def get(self, request):
        return render(
            request,
            self.template_name,
            {"form": CableCalForm(), "formset": CableLineItemFormSet()},
        )

    def post(self, request):
        form = CableCalForm(request.POST)
        formset = CableLineItemFormSet(request.POST)
        if not form.is_valid() or not formset.is_valid():
            return render(
                request, self.template_name, {"form": form, "formset": formset}
            )

        settings = CalculationSettings.get_solo()
        margin = form.cleaned_data.get("margin_override") or settings.winding_margin_mm
        packing = form.cleaned_data.get("packing_override") or settings.packing_factor
        adapter = SimpleNamespace(
            winding_margin_mm=margin,
            packing_factor=packing,
            bending_radius_multiplier=settings.bending_radius_multiplier,
        )
        transport = form.cleaned_data["transport"]
        reels = list(ReelsList.objects.all())

        results = []
        errors = []
        for index, line_form in enumerate(formset):
            cleaned = line_form.cleaned_data
            if cleaned.get("DELETE") or not cleaned.get("diameter"):
                continue
            line = line_form.save(commit=False)
            try:
                results.append((line_form, compute_line(line, reels, adapter, transport)))
            except CalculationError as exc:
                errors.append(_("Row %(n)s: %(err)s") % {"n": index + 1, "err": str(exc)})

        if errors or not results:
            for exc in errors:
                messages.error(request, exc)
            if not results:
                messages.error(request, _("Add at least one cable line."))
            return render(
                request, self.template_name, {"form": form, "formset": formset}
            )

        with transaction.atomic():  # type: ignore
            calc = form.save()
            for position, (line_form, result) in enumerate(results):
                item = line_form.save(commit=False)
                item.cable_cal = calc
                item.position = position
                item.reel_id = result.reel_pk
                item.reel_len = result.reel_len
                item.reel_num = result.reel_num
                item.netto_1 = result.netto_1
                item.brutto_1 = result.brutto_1
                item.netto_all = result.netto_all
                item.brutto_all = result.brutto_all
                item.bending_radius = result.bending_radius
                item.warning = result.warning or ""
                item.save()
        return redirect(calc.get_absolute_url())


class CableCalList(ListView):
    model = CableCal
    template_name = "app/cable_cal_list.html"
    context_object_name = "cable_cal"


class CableCalDetail(DetailView):
    model = CableCal
    template_name = "app/cable_cal_detail.html"
    context_object_name = "cable_cal"


class CableCalDel(DeleteView):
    model = CableCal
    template_name = "app/cable_cal_del.html"
    success_url = reverse_lazy("app:cable_list")


class ReelsListView(ListView):
    model = ReelsList
    template_name = "app/reels.html"
    context_object_name = "reels"


class ReelsListDetail(DetailView):
    model = ReelsList
    template_name = "app/reels_detail.html"
    context_object_name = "reels"


class ReelsListCreate(CreateView):
    form_class = ReelsListForm
    template_name = "app/reels_add.html"
    success_url = reverse_lazy("app:reels_list")


class ReelsListDel(DeleteView):
    model = ReelsList
    template_name = "app/reels_del.html"
    success_url = reverse_lazy("app:reels_list")


class TransportListView(ListView):
    model = TransportList
    template_name = "app/transport.html"
    context_object_name = "transport"


class TransportListDetail(DetailView):
    model = TransportList
    template_name = "app/transport_detail.html"
    context_object_name = "transport"


class TransportListCreate(CreateView):
    form_class = TransportListForm
    template_name = "app/transport_add.html"
    success_url = reverse_lazy("app:transport_list")


class TransportListDel(DeleteView):
    model = TransportList
    template_name = "app/transport_del.html"
    success_url = reverse_lazy("app:transport_list")