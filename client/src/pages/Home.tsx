import { useState, useMemo } from "react";
import { Link } from "wouter";
import { trpc } from "@/lib/trpc";
import { useAuth } from "@/_core/hooks/useAuth";
import { getLoginUrl } from "@/const";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Search,
  MapPin,
  Clock,
  CheckCircle2,
  AlertCircle,
  XCircle,
  PauseCircle,
  HelpCircle,
  Shield,
  LogIn,
  Settings,
  ExternalLink,
} from "lucide-react";

type ImplementationStatus = 
  | "not_implemented"
  | "pending_approval"
  | "approved_not_active"
  | "active"
  | "suspended"
  | "terminated";

const statusConfig: Record<ImplementationStatus, { label: string; icon: React.ElementType; className: string }> = {
  active: { label: "Active", icon: CheckCircle2, className: "status-active" },
  pending_approval: { label: "Pending Approval", icon: Clock, className: "status-pending" },
  approved_not_active: { label: "Approved (Not Active)", icon: AlertCircle, className: "status-pending" },
  suspended: { label: "Suspended", icon: PauseCircle, className: "status-suspended" },
  terminated: { label: "Terminated", icon: XCircle, className: "status-terminated" },
  not_implemented: { label: "Not Implemented", icon: HelpCircle, className: "status-not-implemented" },
};

function StatusBadge({ status }: { status: ImplementationStatus }) {
  const config = statusConfig[status];
  const Icon = config.icon;
  
  return (
    <Badge variant="secondary" className={`${config.className} gap-1 font-medium`}>
      <Icon className="h-3 w-3" />
      {config.label}
    </Badge>
  );
}

function StateCard({ state }: { state: {
  stateCode: string;
  stateName: string;
  implementationStatus: ImplementationStatus;
  summary: string | null;
  weeklyHoursRequired: number | null;
  updatedAt: Date;
}}) {
  return (
    <Link href={`/state/${state.stateCode}`}>
      <Card className="card-hover cursor-pointer h-full">
        <CardHeader className="pb-2">
          <div className="flex items-start justify-between gap-2">
            <div className="flex items-center gap-2">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary font-bold">
                {state.stateCode}
              </div>
              <CardTitle className="text-lg">{state.stateName}</CardTitle>
            </div>
            <StatusBadge status={state.implementationStatus} />
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
            {state.summary || "No information available yet."}
          </p>
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            {state.weeklyHoursRequired && (
              <span className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                {state.weeklyHoursRequired} hrs/week
              </span>
            )}
            <span className="flex items-center gap-1 ml-auto">
              Updated {new Date(state.updatedAt).toLocaleDateString()}
            </span>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}

function StatsCard({ title, value, icon: Icon, description }: {
  title: string;
  value: number;
  icon: React.ElementType;
  description: string;
}) {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
            <Icon className="h-6 w-6 text-primary" />
          </div>
          <div>
            <p className="text-2xl font-bold">{value}</p>
            <p className="text-sm text-muted-foreground">{title}</p>
          </div>
        </div>
        <p className="mt-2 text-xs text-muted-foreground">{description}</p>
      </CardContent>
    </Card>
  );
}

export default function Home() {
  const { user, loading: authLoading } = useAuth();
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  
  const { data: states, isLoading } = trpc.states.list.useQuery();
  const { data: stats } = trpc.states.stats.useQuery();
  
  const filteredStates = useMemo(() => {
    if (!states) return [];
    
    return states.filter((state) => {
      const matchesSearch = 
        state.stateName.toLowerCase().includes(searchQuery.toLowerCase()) ||
        state.stateCode.toLowerCase().includes(searchQuery.toLowerCase());
      
      const matchesStatus = 
        statusFilter === "all" || state.implementationStatus === statusFilter;
      
      return matchesSearch && matchesStatus;
    });
  }, [states, searchQuery, statusFilter]);

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container flex h-16 items-center justify-between">
          <div className="flex items-center gap-3">
            <Shield className="h-8 w-8 text-primary" />
            <div>
              <h1 className="font-semibold text-lg leading-tight">Medicaid Work Requirements</h1>
              <p className="text-xs text-muted-foreground">State-by-State Monitor</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {!authLoading && (
              user ? (
                <div className="flex items-center gap-2">
                  {user.role === "admin" && (
                    <Link href="/admin">
                      <Button variant="outline" size="sm" className="gap-2">
                        <Settings className="h-4 w-4" />
                        Admin
                      </Button>
                    </Link>
                  )}
                  <span className="text-sm text-muted-foreground">{user.name || user.email}</span>
                </div>
              ) : (
                <a href={getLoginUrl()}>
                  <Button variant="outline" size="sm" className="gap-2">
                    <LogIn className="h-4 w-4" />
                    Sign In
                  </Button>
                </a>
              )
            )}
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="gradient-hero py-12 md:py-16">
        <div className="container">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">
              Track Medicaid Work Requirements
              <span className="text-primary"> Across All States</span>
            </h2>
            <p className="text-lg text-muted-foreground mb-8">
              Stay informed about work requirements, exemptions, and reporting procedures 
              for Medicaid programs in your state. Updated weekly with the latest policy changes.
            </p>
            
            {/* Search and Filter */}
            <div className="flex flex-col sm:flex-row gap-3 max-w-xl mx-auto">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search by state name..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 bg-card"
                />
              </div>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-full sm:w-[180px] bg-card">
                  <SelectValue placeholder="Filter by status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Statuses</SelectItem>
                  <SelectItem value="active">Active</SelectItem>
                  <SelectItem value="pending_approval">Pending Approval</SelectItem>
                  <SelectItem value="approved_not_active">Approved (Not Active)</SelectItem>
                  <SelectItem value="suspended">Suspended</SelectItem>
                  <SelectItem value="terminated">Terminated</SelectItem>
                  <SelectItem value="not_implemented">Not Implemented</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-8 border-b">
        <div className="container">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatsCard
              title="Total States"
              value={stats?.totalCount || 51}
              icon={MapPin}
              description="50 states + DC monitored"
            />
            <StatsCard
              title="Active Programs"
              value={stats?.statusCounts?.active || 0}
              icon={CheckCircle2}
              description="Currently enforcing requirements"
            />
            <StatsCard
              title="Pending/Suspended"
              value={(stats?.statusCounts?.pending_approval || 0) + (stats?.statusCounts?.suspended || 0)}
              icon={Clock}
              description="Awaiting implementation"
            />
            <StatsCard
              title="Not Implemented"
              value={stats?.statusCounts?.not_implemented || 0}
              icon={HelpCircle}
              description="No work requirements"
            />
          </div>
        </div>
      </section>

      {/* States Grid */}
      <section className="py-8">
        <div className="container">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-semibold">
              {statusFilter === "all" ? "All States" : `States: ${statusConfig[statusFilter as ImplementationStatus]?.label}`}
              <span className="text-muted-foreground font-normal ml-2">
                ({filteredStates.length})
              </span>
            </h3>
          </div>
          
          {isLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Array.from({ length: 9 }).map((_, i) => (
                <Card key={i} className="h-[160px] animate-pulse">
                  <CardContent className="pt-6">
                    <div className="h-4 bg-muted rounded w-3/4 mb-4" />
                    <div className="h-3 bg-muted rounded w-full mb-2" />
                    <div className="h-3 bg-muted rounded w-2/3" />
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : filteredStates.length === 0 ? (
            <Card className="py-12">
              <CardContent className="text-center">
                <HelpCircle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h4 className="text-lg font-medium mb-2">No states found</h4>
                <p className="text-muted-foreground">
                  Try adjusting your search or filter criteria.
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredStates.map((state, index) => (
                <div key={state.stateCode} className="stagger-item" style={{ animationDelay: `${index * 0.02}s` }}>
                  <StateCard state={state as Parameters<typeof StateCard>[0]["state"]} />
                </div>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-8 mt-8">
        <div className="container">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Shield className="h-4 w-4" />
              <span>Medicaid Work Requirements Monitor</span>
            </div>
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <a 
                href="https://www.medicaid.gov/" 
                target="_blank" 
                rel="noopener noreferrer"
                className="flex items-center gap-1 hover:text-foreground transition-colors"
              >
                Medicaid.gov
                <ExternalLink className="h-3 w-3" />
              </a>
              <a 
                href="https://www.kff.org/medicaid/" 
                target="_blank" 
                rel="noopener noreferrer"
                className="flex items-center gap-1 hover:text-foreground transition-colors"
              >
                KFF Resources
                <ExternalLink className="h-3 w-3" />
              </a>
            </div>
          </div>
          <p className="text-xs text-muted-foreground text-center mt-4">
            Data is updated weekly. For official information, please consult your state's Medicaid agency.
          </p>
        </div>
      </footer>
    </div>
  );
}
