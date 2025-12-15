import { Link, useParams } from "wouter";
import { trpc } from "@/lib/trpc";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  ArrowLeft,
  Clock,
  CheckCircle2,
  AlertCircle,
  XCircle,
  PauseCircle,
  HelpCircle,
  Phone,
  Mail,
  Globe,
  Building2,
  Calendar,
  FileText,
  Shield,
  ExternalLink,
  History,
  Briefcase,
  UserCheck,
} from "lucide-react";

type ImplementationStatus = 
  | "not_implemented"
  | "pending_approval"
  | "approved_not_active"
  | "active"
  | "suspended"
  | "terminated";

const statusConfig: Record<ImplementationStatus, { label: string; icon: React.ElementType; className: string; description: string }> = {
  active: { 
    label: "Active", 
    icon: CheckCircle2, 
    className: "status-active",
    description: "Work requirements are currently being enforced"
  },
  pending_approval: { 
    label: "Pending Approval", 
    icon: Clock, 
    className: "status-pending",
    description: "Waiver application is pending CMS approval"
  },
  approved_not_active: { 
    label: "Approved (Not Active)", 
    icon: AlertCircle, 
    className: "status-pending",
    description: "CMS approved but not yet implemented"
  },
  suspended: { 
    label: "Suspended", 
    icon: PauseCircle, 
    className: "status-suspended",
    description: "Program temporarily suspended"
  },
  terminated: { 
    label: "Terminated", 
    icon: XCircle, 
    className: "status-terminated",
    description: "Program has been terminated or struck down"
  },
  not_implemented: { 
    label: "Not Implemented", 
    icon: HelpCircle, 
    className: "status-not-implemented",
    description: "State has no work requirements program"
  },
};

function InfoSection({ title, icon: Icon, children }: { 
  title: string; 
  icon: React.ElementType; 
  children: React.ReactNode;
}) {
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
        <Icon className="h-4 w-4" />
        {title}
      </div>
      {children}
    </div>
  );
}

function ListItems({ items, emptyText }: { items: string[] | null; emptyText: string }) {
  if (!items || items.length === 0) {
    return <p className="text-sm text-muted-foreground italic">{emptyText}</p>;
  }
  
  return (
    <ul className="space-y-1.5">
      {items.map((item, index) => (
        <li key={index} className="flex items-start gap-2 text-sm">
          <CheckCircle2 className="h-4 w-4 text-primary mt-0.5 shrink-0" />
          <span>{item}</span>
        </li>
      ))}
    </ul>
  );
}

export default function StateDetail() {
  const params = useParams<{ code: string }>();
  const stateCode = params.code?.toUpperCase() || "";
  
  const { data: state, isLoading, error } = trpc.states.byCode.useQuery(
    { code: stateCode },
    { enabled: !!stateCode }
  );
  
  const { data: updates } = trpc.states.updates.useQuery(
    { code: stateCode, limit: 10 },
    { enabled: !!stateCode }
  );

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container py-8">
          <div className="animate-pulse space-y-6">
            <div className="h-8 bg-muted rounded w-48" />
            <div className="h-64 bg-muted rounded" />
            <div className="h-48 bg-muted rounded" />
          </div>
        </div>
      </div>
    );
  }

  if (error || !state) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container py-8">
          <Link href="/">
            <Button variant="ghost" className="gap-2 mb-6">
              <ArrowLeft className="h-4 w-4" />
              Back to all states
            </Button>
          </Link>
          <Card className="py-12">
            <CardContent className="text-center">
              <AlertCircle className="h-12 w-12 text-destructive mx-auto mb-4" />
              <h2 className="text-xl font-semibold mb-2">State Not Found</h2>
              <p className="text-muted-foreground">
                We couldn't find information for state code "{stateCode}".
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  const statusInfo = statusConfig[state.implementationStatus as ImplementationStatus];
  const StatusIcon = statusInfo.icon;

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container flex h-16 items-center">
          <Link href="/">
            <Button variant="ghost" className="gap-2">
              <ArrowLeft className="h-4 w-4" />
              Back
            </Button>
          </Link>
          <div className="flex items-center gap-2 ml-4">
            <Shield className="h-6 w-6 text-primary" />
            <span className="font-medium">Medicaid Work Requirements Monitor</span>
          </div>
        </div>
      </header>

      <main className="container py-8">
        {/* State Header */}
        <div className="mb-8">
          <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="flex h-16 w-16 items-center justify-center rounded-xl bg-primary/10 text-primary text-2xl font-bold">
                {state.stateCode}
              </div>
              <div>
                <h1 className="text-3xl font-bold">{state.stateName}</h1>
                <p className="text-muted-foreground">Medicaid Work Requirements</p>
              </div>
            </div>
            <Badge className={`${statusInfo.className} text-sm px-4 py-2 gap-2`}>
              <StatusIcon className="h-4 w-4" />
              {statusInfo.label}
            </Badge>
          </div>
          <p className="mt-4 text-muted-foreground">{statusInfo.description}</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Summary */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  Summary
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-foreground leading-relaxed">
                  {state.summary || "No summary information available for this state."}
                </p>
                {state.additionalNotes && (
                  <div className="mt-4 p-4 bg-muted/50 rounded-lg">
                    <p className="text-sm text-muted-foreground">{state.additionalNotes}</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Work Hour Requirements */}
            {(state.weeklyHoursRequired || state.monthlyHoursRequired || state.hoursDescription) && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Clock className="h-5 w-5" />
                    Work Hour Requirements
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    {state.weeklyHoursRequired && (
                      <div className="p-4 bg-primary/5 rounded-lg text-center">
                        <p className="text-3xl font-bold text-primary">{state.weeklyHoursRequired}</p>
                        <p className="text-sm text-muted-foreground">Hours per Week</p>
                      </div>
                    )}
                    {state.monthlyHoursRequired && (
                      <div className="p-4 bg-primary/5 rounded-lg text-center">
                        <p className="text-3xl font-bold text-primary">{state.monthlyHoursRequired}</p>
                        <p className="text-sm text-muted-foreground">Hours per Month</p>
                      </div>
                    )}
                  </div>
                  {state.hoursDescription && (
                    <p className="text-sm text-muted-foreground">{state.hoursDescription}</p>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Qualifying Activities */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Briefcase className="h-5 w-5" />
                  Qualifying Activities
                </CardTitle>
                <CardDescription>
                  Activities that count toward meeting work requirements
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ListItems 
                  items={state.qualifyingActivities as string[] | null} 
                  emptyText="No qualifying activities specified for this state."
                />
              </CardContent>
            </Card>

            {/* Exemptions */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <UserCheck className="h-5 w-5" />
                  Exemptions
                </CardTitle>
                <CardDescription>
                  Categories of individuals exempt from work requirements
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ListItems 
                  items={state.exemptions as string[] | null} 
                  emptyText="No exemptions specified for this state."
                />
              </CardContent>
            </Card>

            {/* Reporting Requirements */}
            {(state.reportingFrequency || state.reportingMethod || state.reportingDeadline) && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Calendar className="h-5 w-5" />
                    Reporting Requirements
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {state.reportingFrequency && (
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Frequency</p>
                      <p>{state.reportingFrequency}</p>
                    </div>
                  )}
                  {state.reportingMethod && (
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Method</p>
                      <p>{state.reportingMethod}</p>
                    </div>
                  )}
                  {state.reportingDeadline && (
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Deadline</p>
                      <p>{state.reportingDeadline}</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Contact Information */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Building2 className="h-5 w-5" />
                  Contact Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {state.agencyName && (
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Agency</p>
                    <p className="font-medium">{state.agencyName}</p>
                  </div>
                )}
                {state.agencyPhone && (
                  <div className="flex items-center gap-2">
                    <Phone className="h-4 w-4 text-muted-foreground" />
                    <a href={`tel:${state.agencyPhone}`} className="text-primary hover:underline">
                      {state.agencyPhone}
                    </a>
                  </div>
                )}
                {state.agencyEmail && (
                  <div className="flex items-center gap-2">
                    <Mail className="h-4 w-4 text-muted-foreground" />
                    <a href={`mailto:${state.agencyEmail}`} className="text-primary hover:underline">
                      {state.agencyEmail}
                    </a>
                  </div>
                )}
                {state.agencyWebsite && (
                  <div className="flex items-center gap-2">
                    <Globe className="h-4 w-4 text-muted-foreground" />
                    <a 
                      href={state.agencyWebsite} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-primary hover:underline flex items-center gap-1"
                    >
                      Official Website
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  </div>
                )}
                {!state.agencyName && !state.agencyPhone && !state.agencyEmail && !state.agencyWebsite && (
                  <p className="text-sm text-muted-foreground italic">
                    Contact information not available.
                  </p>
                )}
              </CardContent>
            </Card>

            {/* Key Dates */}
            {(state.approvalDate || state.effectiveDate || state.nextDeadline) && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-lg">
                    <Calendar className="h-5 w-5" />
                    Key Dates
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {state.approvalDate && (
                    <div>
                      <p className="text-sm text-muted-foreground">CMS Approval</p>
                      <p className="font-medium">{new Date(state.approvalDate).toLocaleDateString()}</p>
                    </div>
                  )}
                  {state.effectiveDate && (
                    <div>
                      <p className="text-sm text-muted-foreground">Effective Date</p>
                      <p className="font-medium">{new Date(state.effectiveDate).toLocaleDateString()}</p>
                    </div>
                  )}
                  {state.nextDeadline && (
                    <div>
                      <p className="text-sm text-muted-foreground">Next Deadline</p>
                      <p className="font-medium">{new Date(state.nextDeadline).toLocaleDateString()}</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Source */}
            {state.primarySourceUrl && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-lg">
                    <FileText className="h-5 w-5" />
                    Source
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <a 
                    href={state.primarySourceUrl} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-primary hover:underline flex items-center gap-1 text-sm"
                  >
                    View Primary Source
                    <ExternalLink className="h-3 w-3" />
                  </a>
                  {state.lastVerifiedAt && (
                    <p className="text-xs text-muted-foreground mt-2">
                      Last verified: {new Date(state.lastVerifiedAt).toLocaleDateString()}
                    </p>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Recent Updates */}
            {updates && updates.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-lg">
                    <History className="h-5 w-5" />
                    Recent Updates
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {updates.slice(0, 5).map((update) => (
                      <div key={update.id} className="text-sm border-l-2 border-primary/20 pl-3">
                        <p className="font-medium">{update.fieldChanged}</p>
                        <p className="text-muted-foreground text-xs">
                          {new Date(update.createdAt).toLocaleDateString()}
                        </p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Last Updated */}
            <div className="text-center text-sm text-muted-foreground">
              <p>Last updated: {new Date(state.updatedAt).toLocaleDateString()}</p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t py-6 mt-8">
        <div className="container text-center text-sm text-muted-foreground">
          <p>For official information, please contact your state's Medicaid agency directly.</p>
        </div>
      </footer>
    </div>
  );
}
