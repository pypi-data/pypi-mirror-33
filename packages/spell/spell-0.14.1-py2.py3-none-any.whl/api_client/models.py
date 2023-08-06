import abc
import decimal
import datetime


class Model(object):
    __metaclass__ = abc.ABCMeta

    compare_fields = abc.abstractproperty()

    def __eq__(self, other):
        if not hasattr(other, "__dict__"):
            return False
        my_items = filter(lambda x: x[0] in self.compare_fields, self.__dict__.items())
        other_items = filter(lambda x: x[0] in self.compare_fields, other.__dict__.items())
        return set(my_items) == set(other_items)

    def __hash__(self):
        my_items = filter(lambda x: x[0] in self.compare_fields, self.__dict__.items())
        return hash(tuple(sorted(my_items)))


class User(Model):

    compare_fields = ["email", "user_name", "full_name", "created_at"]

    def __init__(self, email, user_name, created_at, updated_at,
                 full_name=None, last_logged_in=None, **kwargs):
        self.email = email
        self.user_name = user_name
        self.full_name = full_name
        self.created_at = created_at
        self.updated_at = updated_at
        self.last_logged_in = last_logged_in


class Key(Model):

    compare_fields = ["id", "title", "fingerprint", "created_at"]

    def __init__(self, id, title, fingerprint, verified, created_at, **kwargs):
        self.id = int(id)
        self.title = title
        self.fingerprint = fingerprint
        self.verified = verified
        self.created_at = created_at


class Workspace(Model):

    compare_fields = ["id", "root_commit", "name", "description", "git_remote_url", "created_at"]

    def __init__(self, id, root_commit, name, description, git_remote_url, created_at, updated_at,
                 git_commit_hash=None, **kwargs):
        self.id = int(id)
        self.root_commit = root_commit
        self.name = name
        self.description = description
        self.git_remote_url = git_remote_url
        self.created_at = created_at
        self.updated_at = updated_at
        self.git_commit_hash = git_commit_hash


class Run(Model):

    compare_fields = ["id", "status", "command", "gpu", "git_commit_hash", "docker_image", "framework", "workspace"]

    def __init__(self, id, status, command, gpu, git_commit_hash, framework, docker_image,
                 created_at, workspace=None, user_exit_code=None, started_at=None, ended_at=None, **kwargs):
        self.id = int(id)
        self.status = status
        self.user_exit_code = user_exit_code
        self.command = command
        self.gpu = gpu
        self.git_commit_hash = git_commit_hash
        self.docker_image = docker_image
        self.framework = framework
        self.created_at = created_at
        self.started_at = started_at
        self.ended_at = ended_at
        self.workspace = workspace


class LsLine(Model):

    compare_fields = ["path", "size"]

    def __init__(self, path, size, date=None, additional_info=None, **kwargs):
        self.path = path
        self.size = size
        self.date = date
        self.additional_info = additional_info


class CPUStats(Model):

    compare_fields = ["cpu_percentage", "memory", "memory_total", "memory_percentage",
                      "network_rx", "network_tx", "block_read", "block_write"]

    def __init__(self, cpu_percentage, memory, memory_total, memory_percentage,
                 network_rx, network_tx, block_read, block_write, **kwargs):
        self.cpu_percentage = cpu_percentage
        self.memory = memory
        self.memory_total = memory_total
        self.memory_percentage = memory_percentage
        self.network_rx = network_rx
        self.network_tx = network_tx
        self.block_read = block_read
        self.block_write = block_write


class GPUStats(Model):

    compare_fields = ["name", "temperature", "power_draw", "power_limit",
                      "gpu_utilization", "memory_utilization", "memory_used", "memory_total", "perf_state"]

    def __init__(self, name, temperature, power_draw, power_limit,
                 gpu_utilization, memory_utilization, memory_used, memory_total, perf_state, **kwargs):
        self.name = name
        self.temperature = temperature
        self.power_draw = power_draw
        self.power_limit = power_limit
        self.gpu_utilization = gpu_utilization
        self.memory_utilization = memory_utilization
        self.memory_used = memory_used
        self.memory_total = memory_total
        self.perf_state = perf_state


class UserDataset(Model):

    compare_fields = ["id", "name", "status", "created_at"]

    def __init__(self, id, name, status, updated_at, created_at, **kwargs):
        self.id = id
        self.name = name
        self.status = status
        self.updated_at = updated_at
        self.created_at = created_at


class Template(Model):

    compare_fields = ["body"]

    def __init__(self, body, **kwargs):
        self.body = body


class Error(Model):

    compare_fields = ["status", "error", "code"]

    def __init__(self, status, error, code):
        self.status = status
        self.error = error
        self.code = code

    @staticmethod
    def response_dict_to_object(obj):
        if "status" in obj or "error" in obj or "code" in obj:
            status = obj.get("status", None)
            error = obj.get("error", None)
            code = obj.get("code", None)
            return Error(status, error, code)
        return obj

    def __str__(self):
        if self.error:
            return self.error
        elif self.status:
            return self.status
        else:
            return None


class MachineStats(Model):
    compare_fields = ["machine_type_name", "time_used", "cost_used_usd"]

    def __init__(self, machine_type_name, time_used, cost_used_cents):
        self.machine_type_name = machine_type_name
        self.time_used = datetime.timedelta(seconds=time_used)
        self.cost_used_usd = decimal.Decimal(cost_used_cents)/100


def parseNullDate(dt):
    if dt is None:
        return None
    return dt.date()


class BillingStatus(Model):
    compare_fields = ["plan_id", "plan_name", "remaining_credits_usd", "period_machine_stats", "total_machine_stats",
                      "last_machine_invoice_date", "next_machine_invoice_date", "total_runs", "concurrent_queued_runs",
                      "concurrent_run_limit", "previous_stripe_billing_date", "next_stripe_billing_date",
                      "used_credit_usd"]

    def __init__(self, plan_id, plan_name, remaining_credit_cents, last_machine_invoice_date,
                 period_machine_stats, total_machine_stats, concurrent_queued_runs,
                 concurrent_run_limit, total_runs, next_machine_invoice_date, previous_stripe_billing_date,
                 next_stripe_billing_date, used_credit_cents, **kwargs):
        self.plan_id = plan_id
        self.plan_name = plan_name
        self.remaining_credits_usd = decimal.Decimal(remaining_credit_cents)/100
        self.used_credits_usd = decimal.Decimal(used_credit_cents)/100
        self.period_machine_stats = [MachineStats(**s) for s in period_machine_stats]
        self.total_machine_stats = [MachineStats(**s) for s in total_machine_stats]
        self.last_machine_invoice_date = parseNullDate(last_machine_invoice_date)
        self.next_machine_invoice_date = parseNullDate(next_machine_invoice_date)
        self.previous_stripe_billing_date = parseNullDate(previous_stripe_billing_date)
        self.next_stripe_billing_date = parseNullDate(next_stripe_billing_date)

        self.total_runs = total_runs
        self.concurrent_queued_runs = concurrent_queued_runs
        self.concurrent_run_limit = concurrent_run_limit
