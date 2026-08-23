from collections import namedtuple

from django.contrib import messages
from django.db import transaction
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, FormView, ListView

from .calc import CalculationError, compute_line  # type: ignore[import-unresolved]
from .forms import CableCalForm, ReelsListForm, TransportListForm
from .models import CableCal, ReelsList, TransportList

# Default winding parameters. Replaced by the CalculationSettings singleton
# in Phase 2 (data-model normalization), kept here so the formula fix lands
# before the model refactor.
WINDING_MARGIN_MM = 50.0
PACKING_FACTOR = 0.93
BENDING_RADIUS_MULTIPLIER = 10.0


class _CalcSettings:
    """Lightweight settings adapter consumed by :func:`compute_line`."""

    winding_margin_mm = WINDING_MARGIN_MM
    packing_factor = PACKING_FACTOR
    bending_radius_multiplier = BENDING_RADIUS_MULTIPLIER


_Line = namedtuple(
    "_Line",
    ["cod", "name", "con_num", "order_len", "max_len", "mass", "diameter"],
)


class CableCalView(FormView):
    template_name = "app/cable_cal.html"
    form_class = CableCalForm

    def get_success_url(self):
        pk = self.object.pk
        return reverse("cable_detail", kwargs={"pk": pk})

    def form_valid(self, form):
        transport = form.cleaned_data["transport"]
        reels = list(ReelsList.objects.all())  # type: ignore[attr-defined]
        settings = _CalcSettings()

        cods = self.request.POST.getlist("cod")
        names = self.request.POST.getlist("name")
        order_lens = self.request.POST.getlist("order_len")
        masses = self.request.POST.getlist("mass")
        diameters = self.request.POST.getlist("diameter")
        con_nums = self.request.POST.getlist("con_num")
        max_lens = self.request.POST.getlist("max_len")

        results = []
        errors = []
        for index, (cod, name, olen, mass, dia, con, mlen) in enumerate(
            zip(cods, names, order_lens, masses, diameters, con_nums, max_lens)
        ):
            line = _Line(cod, name, con, olen, mlen, mass, dia)
            try:
                results.append(compute_line(line, reels, settings, transport))
            except CalculationError as exc:
                errors.append(f"Row {index + 1}: {exc}")

        if errors:
            for exc in errors:
                messages.error(self.request, exc)
            return self.form_invalid(form)

        def _join(selector):
            return "\n".join(str(selector(result)) for result in results)

        with transaction.atomic():  # type: ignore
            self.object = CableCal.objects.create(  # type: ignore[attr-defined]
                order_num=form.cleaned_data["order_num"],
                transport=transport,
                cod="\n".join(cods),
                name="\n".join(names),
                order_len="\n".join(order_lens),
                mass="\n".join(masses),
                diameter="\n".join(diameters),
                con_num="\n".join(con_nums),
                max_len="\n".join(max_lens),
                reel_name=_join(lambda r: r.reel_name),
                reel_num=_join(lambda r: r.reel_num),
                reel_len=_join(lambda r: r.reel_len),
                netto_1=_join(lambda r: r.netto_1),
                brutto_1=_join(lambda r: r.brutto_1),
                netto_all=_join(lambda r: r.netto_all),
                brutto_all=_join(lambda r: r.brutto_all),
                bending_radius=_join(lambda r: r.bending_radius),
            )
        return super().form_valid(form)


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
    success_url = reverse_lazy("cable_list")


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
    success_url = reverse_lazy("reels_list")


class ReelsListDel(DeleteView):
    model = ReelsList
    template_name = "app/reels_del.html"
    success_url = reverse_lazy("reels_list")


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
    success_url = reverse_lazy("transport_list")


class TransportListDel(DeleteView):
    model = TransportList
    template_name = "app/transport_del.html"
    success_url = reverse_lazy("transport_list")