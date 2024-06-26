<template>
	<Dialog
		v-if="role.doc"
		:options="{ title: `${role.doc.title}` }"
		v-model="show"
		@after-leave="() => (this.memberEmail = '')"
	>
		<template v-slot:body-content>
			<div class="rounded border-2 border-dashed p-3 text-base">
				<div class="mb-4 flex gap-2">
					<div class="flex-1">
						<Autocomplete
							:options="autoCompleteList"
							v-model="member"
							placeholder="Select a member to add"
						/>
					</div>
					<Button
						variant="solid"
						label="Add Member"
						:disabled="!member?.value"
						:loading="role.addUser?.loading"
						@click="() => addUser(member.value)"
					/>
				</div>
				<div>
					<div class="mb-1 text-gray-600">Members</div>
					<div
						v-if="roleUsers.length === 0"
						class="p-4 text-center text-gray-500"
					>
						<span>No members added to this role.</span>
					</div>
					<div v-else class="flex flex-col divide-y">
						<div v-for="user in roleUsers" class="flex justify-between py-2.5">
							<UserWithAvatarCell
								:avatarImage="user.user_image"
								:fullName="user.full_name"
								:email="user.user"
								:key="user.user"
							/>
							<Button @click="() => removeUser(user.user)">
								<template #icon>
									<i-lucide-x class="h-4 w-4 text-gray-600" />
								</template>
							</Button>
						</div>
					</div>
				</div>
			</div>
			<div class="mt-4 rounded border-2 border-dashed p-3 text-base">
				<div class="mb-2 text-gray-600">Global Permissions</div>
				<div class="flex flex-col space-y-2">
					<FormControl
						type="checkbox"
						v-model="enableBilling"
						label="Allow Access to Billing"
					/>
					<FormControl
						type="checkbox"
						v-model="enableApps"
						label="Allow Access to Apps"
					/>
				</div>
			</div>
		</template>
	</Dialog>
</template>

<script setup>
import { createDocumentResource } from 'frappe-ui';
import { computed, ref, watch } from 'vue';
import { getTeam } from '../../data/team';
import UserWithAvatarCell from '../UserWithAvatarCell.vue';
import { toast } from 'vue-sonner';
import session from '../../data/session';

const props = defineProps({
	roleId: { type: String, required: true }
});
const member = ref({});
const show = ref(true);

const role = createDocumentResource({
	doctype: 'Press Role',
	name: props.roleId,
	auto: true,
	whitelistedMethods: {
		addUser: 'add_user',
		removeUser: 'remove_user'
	},
	onSuccess: data => {
		enableBilling.value = !!data.enable_billing;
		enableApps.value = !!data.enable_apps;
	}
});
const roleUsers = computed(() => role.doc.users || []);
const enableBilling = ref(!!role.doc?.enable_billing);
const enableApps = ref(!!role.doc?.enable_apps);

// using a watcher instead of event listener to avoid multiple api calls
watch(enableBilling, () => {
	if (enableBilling.value === !!role.doc.enable_billing) return;

	role.setValue.submit(
		{ enable_billing: enableBilling.value },
		{ onSuccess: session.roles.reload }
	);
});
watch(enableApps, () => {
	if (enableApps.value === !!role.doc.enable_apps) return;

	role.setValue.submit(
		{ enable_apps: enableApps.value },
		{ onSuccess: session.roles.reload }
	);
});

const team = getTeam();
const autoCompleteList = computed(() => {
	const isNotGroupMember = u =>
		!roleUsers.value.map(({ user }) => user).includes(u);
	return team.doc.team_members
		?.filter(({ user }) => isNotGroupMember(user))
		.map(({ user }) => ({ label: user, value: user }));
});

function addUser(user) {
	return toast.promise(role.addUser.submit({ user }), {
		loading: `Adding ${user} to ${role.doc.title}`,
		success: () => {
			member.value = {};
			return `${user} added to ${role.doc.title}`;
		},
		error: e => (e.messages.length ? e.messages.join('\n') : e.message)
	});
}

function removeUser(user) {
	return toast.promise(role.removeUser.submit({ user }), {
		loading: `Removing ${user} from ${role.doc.title}`,
		success: () => {
			return `${user} removed from ${role.doc.title}`;
		},
		error: e => (e.messages.length ? e.messages.join('\n') : e.message)
	});
}
</script>
